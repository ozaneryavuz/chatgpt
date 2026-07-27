from __future__ import annotations

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

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
