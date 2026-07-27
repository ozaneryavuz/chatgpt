from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import create_engine, event, func, inspect, select, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


engine_kwargs: dict[str, object] = {
    "pool_pre_ping": True,
    "pool_recycle": 1_800,
}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)

if settings.database_url.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def _aware(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


@event.listens_for(Session, "before_flush")
def _continuity_integrity_guards(session: Session, _flush_context, _instances) -> None:
    """Endpoint katmanındaki üç kritik bütünlük kuralını son savunma hattında korur.

    Bu guardlar aynı davranışı SQLite ve PostgreSQL altında uygular:
    - kuruluşun son admin'i rol düşüremez,
    - geçmiş tarihli test `last_test_at` değerini geriye götüremez,
    - kapalı olay tekrar kapatıldığında kapanış/audit/e-posta çoğalmaz.
    """
    from .models import (  # geç import, Base/models döngüsünü önler
        Asset,
        AuditLog,
        EmailOutbox,
        Incident,
        Membership,
        Role,
    )

    repeated_closures: set[str] = set()

    for obj in list(session.dirty):
        state = inspect(obj)

        if isinstance(obj, Membership):
            history = state.attrs.role.history
            if history.has_changes() and history.deleted:
                previous = history.deleted[0]
                previous_value = getattr(previous, "value", previous)
                current_value = getattr(obj.role, "value", obj.role)
                if previous_value == Role.admin.value and current_value != Role.admin.value:
                    remaining_admins = int(
                        session.scalar(
                            select(func.count(Membership.id)).where(
                                Membership.organization_id == obj.organization_id,
                                Membership.id != obj.id,
                                Membership.role == Role.admin,
                            )
                        )
                        or 0
                    )
                    if remaining_admins == 0:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Kuruluşun son yöneticisinin rolü düşürülemez.",
                        )

        elif isinstance(obj, Asset):
            history = state.attrs.last_test_at.history
            if history.has_changes() and history.deleted and obj.last_test_at is not None:
                previous = history.deleted[0]
                if previous is not None and _aware(obj.last_test_at) < _aware(previous):
                    obj.last_test_at = previous

        elif isinstance(obj, Incident):
            ended_history = state.attrs.ended_at.history
            if ended_history.has_changes() and ended_history.deleted:
                previous_ended_at = ended_history.deleted[0]
                if previous_ended_at is not None:
                    repeated_closures.add(obj.id)
                    obj.ended_at = previous_ended_at
                    summary_history = state.attrs.summary.history
                    if summary_history.deleted:
                        obj.summary = summary_history.deleted[0]
                    status_history = state.attrs.status.history
                    if status_history.deleted:
                        obj.status = status_history.deleted[0]

    if not repeated_closures:
        return

    # Tekrarlanan kapanışın yeni audit ve olay e-postası üretmesini engelle.
    for obj in list(session.new):
        if isinstance(obj, AuditLog) and obj.action == "incident.closed" and obj.entity_id in repeated_closures:
            session.expunge(obj)
            continue
        if isinstance(obj, EmailOutbox) and obj.template == "incident_event":
            try:
                from .security import decrypt_secret

                payload = json.loads(decrypt_secret(obj.payload_json))
            except Exception:  # pragma: no cover - bozuk payload başka doğrulamalara bırakılır
                continue
            if payload.get("incident_id") in repeated_closures and payload.get("action") == "Olay kapatıldı":
                session.expunge(obj)


def init_db() -> None:
    if not settings.auto_create_schema:
        return
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_db() -> None:
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))


def database_ready() -> bool:
    """Production readiness endpointi için geriye uyumlu, yan etkisiz DB kontrolü."""
    try:
        check_db()
        return True
    except Exception:
        return False
