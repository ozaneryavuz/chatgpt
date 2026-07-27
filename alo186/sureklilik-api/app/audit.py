from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuditLog


def write_audit(
    db: Session,
    *,
    organization_id: str,
    user_id: str | None,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict | None = None,
) -> None:
    # Olay kapanışı ağ tekrarları veya istemci retry'larıyla ikinci kez çağrılsa bile
    # tarihsel audit zincirinde aynı olaya ait tek kapanış kaydı tutulur.
    if action == "incident.closed":
        existing = db.scalar(
            select(AuditLog.id).where(
                AuditLog.organization_id == organization_id,
                AuditLog.action == action,
                AuditLog.entity_type == entity_type,
                AuditLog.entity_id == entity_id,
            )
        )
        if existing:
            return
    db.add(
        AuditLog(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details_json=json.dumps(details, ensure_ascii=False) if details else None,
        )
    )
