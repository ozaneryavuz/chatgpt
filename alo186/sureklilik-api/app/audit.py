from __future__ import annotations

import json

from sqlalchemy.orm import Session

from .models import AuditLog


def write_audit(
    db: Session,
    *,
    organization_id: str,
    user_id: str,
    action: str,
    entity_type: str,
    entity_id: str,
    details: dict | None = None,
) -> None:
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
