from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import event, func, inspect, select
from sqlalchemy.orm import Session

from .models import (
    Asset,
    AuditLog,
    CriticalLoad,
    EmailOutbox,
    Incident,
    IncidentStatus,
    IncidentTask,
    Membership,
    Priority,
    Role,
)


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    return slug or "kurulus"


def unique_slug(db: Session, name: str, model) -> str:
    base = slugify(name)
    candidate = base
    suffix = 2
    while db.scalar(select(model.id).where(model.slug == candidate)):
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def build_incident_tasks(
    db: Session,
    *,
    organization_id: str,
    incident_id: str,
    location_id: str,
) -> list[IncidentTask]:
    tasks = [
        IncidentTask(
            organization_id=organization_id,
            incident_id=incident_id,
            title="Can güvenliği, yangın, duman ve düşmüş iletken riskini kontrol et",
            priority=Priority.p1,
            is_required=True,
        ),
        IncidentTask(
            organization_id=organization_id,
            incident_id=incident_id,
            title="Kesintinin şebeke, bina veya tesis içi kapsamını doğrula",
            priority=Priority.p1,
            is_required=True,
        ),
        IncidentTask(
            organization_id=organization_id,
            incident_id=incident_id,
            title="Olay başlangıç saatini ve resmî kayıt numarasını kaydet",
            priority=Priority.p2,
            is_required=False,
        ),
    ]
    loads = db.scalars(
        select(CriticalLoad).where(
            CriticalLoad.organization_id == organization_id,
            CriticalLoad.location_id == location_id,
            CriticalLoad.priority == Priority.p1,
        )
    ).all()
    for load in loads:
        source = load.backup_source or "yedek kaynağı"
        tasks.append(
            IncidentTask(
                organization_id=organization_id,
                incident_id=incident_id,
                title=f"{load.name}: {source} devreye alma ve otonomi durumunu doğrula",
                priority=Priority.p1,
                is_required=True,
                assignee_name=load.owner_name,
            )
        )
    return tasks


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _is_duplicate_close_email(item: EmailOutbox, incident_ids: set[str]) -> bool:
    if item.template != "incident_event" or not incident_ids:
        return False
    try:
        # Import işlev içinde tutulur; notifications modülünün model importlarıyla
        # servis katmanı arasında başlangıç zamanı döngüsü oluşmasını önler.
        from .notifications import read_payload

        payload = read_payload(item)
        return (
            str(payload.get("incident_id", "")) in incident_ids
            and str(payload.get("action", "")) == "Olay kapatıldı"
        )
    except Exception:
        # Şifreli payload okunamıyorsa başka bir olaya ait bildirimi yanlışlıkla
        # düşürmek yerine outbox kaydını korur; worker hata kaydı üretecektir.
        return False


@event.listens_for(Session, "before_flush")
def enforce_integrity_guards(session: Session, _flush_context, _instances) -> None:
    """API dışındaki yazma yollarında da kritik bütünlük kurallarını korur.

    CLI, worker ve gelecekteki servis katmanı yazmalarında da son yönetici,
    test tarihi ve olay kapanışı kurallarını uygular.
    """

    repeated_closed_incidents: dict[str, str] = {}

    for item in list(session.dirty):
        if isinstance(item, Membership):
            role_history = inspect(item).attrs.role.history
            if (
                role_history.has_changes()
                and role_history.deleted
                and role_history.deleted[0] == Role.admin
                and item.role != Role.admin
            ):
                admin_count = int(
                    session.scalar(
                        select(func.count(Membership.id)).where(
                            Membership.organization_id == item.organization_id,
                            Membership.role == Role.admin,
                        )
                    )
                    or 0
                )
                if admin_count <= 1:
                    raise HTTPException(
                        status_code=409,
                        detail="Kuruluşun son yöneticisinin rolü düşürülemez.",
                    )

        if isinstance(item, Asset):
            history = inspect(item).attrs.last_test_at.history
            if history.has_changes() and history.deleted and history.added:
                previous = history.deleted[0]
                proposed = history.added[0]
                if previous is not None and proposed is not None and _aware(proposed) < _aware(previous):
                    item.last_test_at = previous

        if isinstance(item, Incident) and item.status == IncidentStatus.closed:
            state = inspect(item)
            status_history = state.attrs.status.history
            ended_history = state.attrs.ended_at.history
            if not status_history.has_changes() and ended_history.deleted and ended_history.added:
                previous_ended_at = ended_history.deleted[0]
                if previous_ended_at is not None:
                    item.ended_at = previous_ended_at
                    summary_history = state.attrs.summary.history
                    if summary_history.deleted:
                        item.summary = summary_history.deleted[0]
                    repeated_closed_incidents[item.id] = item.organization_id

    if repeated_closed_incidents:
        incident_ids = set(repeated_closed_incidents)
        for item in list(session.new):
            if (
                isinstance(item, AuditLog)
                and item.action == "incident.closed"
                and item.entity_id in incident_ids
            ):
                session.expunge(item)
            elif isinstance(item, EmailOutbox) and _is_duplicate_close_email(item, incident_ids):
                session.expunge(item)
