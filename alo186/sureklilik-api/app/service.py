from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import CriticalLoad, IncidentTask, Priority


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
