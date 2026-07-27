from __future__ import annotations

from datetime import timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Asset, CriticalLoad, Location, Membership, Organization, utcnow

PLAN_LIMITS: dict[str, dict[str, int | None]] = {
    "pilot": {"locations": 3, "members": 3, "critical_loads": 25, "assets": 10},
    "site": {"locations": 10, "members": 25, "critical_loads": 100, "assets": 30},
    "hotel": {"locations": 10, "members": 50, "critical_loads": 250, "assets": 100},
    "business": {"locations": 20, "members": 50, "critical_loads": 300, "assets": 120},
    "enterprise": {"locations": None, "members": None, "critical_loads": None, "assets": None},
}

RESOURCE_MODELS = {
    "locations": Location,
    "members": Membership,
    "critical_loads": CriticalLoad,
    "assets": Asset,
}


def _aware(value):
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def plan_limits(organization: Organization) -> dict[str, int | None]:
    return PLAN_LIMITS.get(organization.plan, PLAN_LIMITS["pilot"])


def ensure_subscription_writable(organization: Organization) -> None:
    if organization.subscription_status in {"cancelled", "past_due", "suspended"}:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "SUBSCRIPTION_INACTIVE", "message": "Abonelik yazma işlemlerine kapalı."},
        )
    expires_at = _aware(organization.plan_expires_at)
    if expires_at is not None and expires_at < utcnow():
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "PLAN_EXPIRED", "message": "Plan süresi doldu."},
        )


def resource_count(db: Session, organization_id: str, resource: str) -> int:
    model = RESOURCE_MODELS[resource]
    return int(
        db.scalar(select(func.count(model.id)).where(model.organization_id == organization_id)) or 0
    )


def enforce_limit(db: Session, organization: Organization, resource: str, *, increment: int = 1) -> None:
    ensure_subscription_writable(organization)
    limit = plan_limits(organization).get(resource)
    if limit is None:
        return
    current = resource_count(db, organization.id, resource)
    if current + increment > limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "resource": resource,
                "current": current,
                "limit": limit,
                "plan": organization.plan,
            },
        )


def usage_snapshot(db: Session, organization: Organization) -> dict[str, object]:
    limits = plan_limits(organization)
    usage = {resource: resource_count(db, organization.id, resource) for resource in RESOURCE_MODELS}
    return {
        "plan": organization.plan,
        "subscription_status": organization.subscription_status,
        "plan_expires_at": organization.plan_expires_at,
        "usage": usage,
        "limits": limits,
        "remaining": {
            key: None if limits[key] is None else max(0, int(limits[key]) - usage[key])
            for key in usage
        },
    }
