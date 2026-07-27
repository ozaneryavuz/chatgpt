from __future__ import annotations

from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy import delete, func, select, update
from sqlalchemy.orm import Session, selectinload

from .auth_service import revoke_all_sessions
from .config import settings
from .models import (
    Asset,
    AssetTest,
    AuditLog,
    AuthSession,
    AuthToken,
    CriticalLoad,
    EmailOutbox,
    Incident,
    IncidentTask,
    Location,
    Membership,
    Organization,
    Role,
    User,
    utcnow,
)


def user_export(db: Session, user: User) -> dict[str, object]:
    memberships = db.scalars(
        select(Membership)
        .options(selectinload(Membership.organization))
        .where(Membership.user_id == user.id)
    ).all()
    audits = db.scalars(
        select(AuditLog)
        .where(AuditLog.user_id == user.id)
        .order_by(AuditLog.created_at.desc())
        .limit(1_000)
    ).all()
    sessions = db.scalars(
        select(AuthSession)
        .where(AuthSession.user_id == user.id)
        .order_by(AuthSession.created_at.desc())
        .limit(100)
    ).all()
    return {
        "exported_at": utcnow().isoformat(),
        "user": {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "mfa_enabled": user.mfa_enabled,
            "created_at": user.created_at,
            "last_login_at": user.last_login_at,
            "deletion_requested_at": user.deletion_requested_at,
        },
        "memberships": [
            {
                "organization_id": item.organization_id,
                "organization_name": item.organization.name,
                "role": item.role.value,
                "notify_incidents": item.notify_incidents,
                "created_at": item.created_at,
            }
            for item in memberships
        ],
        "sessions": [
            {
                "id": item.id,
                "created_at": item.created_at,
                "last_seen_at": item.last_seen_at,
                "expires_at": item.expires_at,
                "revoked_at": item.revoked_at,
            }
            for item in sessions
        ],
        "audit_actions": [
            {
                "organization_id": item.organization_id,
                "action": item.action,
                "entity_type": item.entity_type,
                "entity_id": item.entity_id,
                "created_at": item.created_at,
            }
            for item in audits
        ],
    }


def organization_export(db: Session, organization: Organization) -> dict[str, object]:
    locations = db.scalars(select(Location).where(Location.organization_id == organization.id)).all()
    loads = db.scalars(select(CriticalLoad).where(CriticalLoad.organization_id == organization.id)).all()
    assets = db.scalars(select(Asset).where(Asset.organization_id == organization.id)).all()
    tests = db.scalars(select(AssetTest).where(AssetTest.organization_id == organization.id)).all()
    incidents = db.scalars(
        select(Incident)
        .options(selectinload(Incident.tasks))
        .where(Incident.organization_id == organization.id)
    ).all()
    memberships = db.scalars(
        select(Membership)
        .options(selectinload(Membership.user))
        .where(Membership.organization_id == organization.id)
    ).all()
    audits = db.scalars(
        select(AuditLog)
        .where(AuditLog.organization_id == organization.id)
        .order_by(AuditLog.created_at)
    ).all()
    return {
        "exported_at": utcnow().isoformat(),
        "organization": {
            "id": organization.id,
            "name": organization.name,
            "slug": organization.slug,
            "plan": organization.plan,
            "subscription_status": organization.subscription_status,
            "created_at": organization.created_at,
        },
        "members": [
            {
                "user_id": item.user_id,
                "email": item.user.email,
                "role": item.role.value,
                "notify_incidents": item.notify_incidents,
            }
            for item in memberships
        ],
        "locations": [_row(item) for item in locations],
        "critical_loads": [_row(item) for item in loads],
        "assets": [_row(item) for item in assets],
        "asset_tests": [_row(item) for item in tests],
        "incidents": [
            {
                **_row(item),
                "status": item.status.value,
                "tasks": [{**_row(task), "priority": task.priority.value, "status": task.status.value} for task in item.tasks],
            }
            for item in incidents
        ],
        "audit_logs": [_row(item) for item in audits],
    }


def _row(item) -> dict[str, object]:
    result: dict[str, object] = {}
    for column in item.__table__.columns:
        value = getattr(item, column.name)
        if hasattr(value, "value"):
            value = value.value
        result[column.name] = value
    return result


def request_user_deletion(db: Session, user: User) -> None:
    admin_memberships = db.scalars(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.role == Role.admin,
        )
    ).all()
    blocking: list[str] = []
    for membership in admin_memberships:
        other_admins = int(
            db.scalar(
                select(func.count(Membership.id)).where(
                    Membership.organization_id == membership.organization_id,
                    Membership.role == Role.admin,
                    Membership.user_id != user.id,
                )
            )
            or 0
        )
        organization = db.get(Organization, membership.organization_id)
        if other_admins == 0 and organization and organization.deletion_requested_at is None:
            blocking.append(organization.name)
    if blocking:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "SOLE_ADMIN",
                "message": "Hesap silmeden önce kuruluş yöneticiliğini devredin veya kuruluş silme talebi oluşturun.",
                "organizations": blocking,
            },
        )
    user.deletion_requested_at = utcnow()
    user.deletion_execute_after = utcnow() + timedelta(days=settings.deletion_grace_days)
    user.is_active = False
    revoke_all_sessions(db, user)
    db.flush()


def request_organization_deletion(db: Session, organization: Organization) -> None:
    organization.deletion_requested_at = utcnow()
    organization.deletion_execute_after = utcnow() + timedelta(days=settings.deletion_grace_days)
    organization.is_active = False
    db.flush()


def _detach_user_references(db: Session, user_id: str) -> None:
    # V0.2 şemalarında FK ON DELETE SET NULL bulunmayabilir. Tarihsel operasyon
    # kayıtlarını koruyup kullanıcı bağlantısını silme öncesinde anonimleştirir.
    db.execute(
        update(AssetTest)
        .where(AssetTest.created_by_user_id == user_id)
        .values(created_by_user_id=None)
    )
    db.execute(
        update(Incident)
        .where(Incident.created_by_user_id == user_id)
        .values(created_by_user_id=None)
    )
    db.execute(
        update(AuditLog)
        .where(AuditLog.user_id == user_id)
        .values(user_id=None)
    )


def purge_due_data(db: Session) -> dict[str, int]:
    now = utcnow()
    token_result = db.execute(
        delete(AuthToken).where(
            (AuthToken.expires_at < now)
            | ((AuthToken.consumed_at.is_not(None)) & (AuthToken.created_at < now - timedelta(days=7)))
        )
    )
    session_result = db.execute(
        delete(AuthSession).where(
            (AuthSession.expires_at < now - timedelta(days=7))
            | ((AuthSession.revoked_at.is_not(None)) & (AuthSession.revoked_at < now - timedelta(days=7)))
        )
    )
    outbox_result = db.execute(
        delete(EmailOutbox).where(
            EmailOutbox.status.in_(["sent", "failed"]),
            EmailOutbox.created_at < now - timedelta(days=settings.outbox_retention_days),
        )
    )
    audit_result = db.execute(
        delete(AuditLog).where(
            AuditLog.created_at < now - timedelta(days=settings.audit_retention_days)
        )
    )
    organizations = db.scalars(
        select(Organization).where(
            Organization.deletion_execute_after.is_not(None),
            Organization.deletion_execute_after <= now,
        )
    ).all()
    users = db.scalars(
        select(User).where(
            User.deletion_execute_after.is_not(None),
            User.deletion_execute_after <= now,
        )
    ).all()
    organization_count = len(organizations)
    user_count = len(users)
    for organization in organizations:
        db.delete(organization)
    db.flush()
    for user in users:
        _detach_user_references(db, user.id)
        db.delete(user)
    db.commit()
    return {
        "auth_tokens": int(token_result.rowcount or 0),
        "sessions": int(session_result.rowcount or 0),
        "outbox": int(outbox_result.rowcount or 0),
        "audit_logs": int(audit_result.rowcount or 0),
        "organizations": organization_count,
        "users": user_count,
    }
