from __future__ import annotations

from datetime import timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth_service import create_session
from .config import settings
from .models import Membership, Organization, OrganizationInvitation, Role, User, utcnow
from .notifications import organization_invitation_email
from .plans import plan_limits
from .security import create_one_time_token, hash_one_time_token, hash_password


def _aware(value):
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def invitation_status(invitation: OrganizationInvitation) -> str:
    if invitation.accepted_at is not None:
        return "accepted"
    if invitation.revoked_at is not None:
        return "revoked"
    if _aware(invitation.expires_at) <= utcnow():
        return "expired"
    return "pending"


def invitation_by_token(db: Session, raw_token: str, *, lock: bool = False) -> OrganizationInvitation:
    query = select(OrganizationInvitation).where(
        OrganizationInvitation.token_hash == hash_one_time_token(raw_token)
    )
    if lock and db.bind and db.bind.dialect.name == "postgresql":
        query = query.with_for_update()
    invitation = db.scalar(query)
    if not invitation or invitation_status(invitation) != "pending":
        raise HTTPException(status_code=400, detail="Davet geçersiz, iptal edilmiş veya süresi dolmuş.")
    return invitation


def ensure_invitation_capacity(
    db: Session,
    organization: Organization,
    *,
    invited_email: str,
) -> None:
    limit = plan_limits(organization).get("members")
    if limit is None:
        return
    members = int(
        db.scalar(
            select(func.count(Membership.id)).where(Membership.organization_id == organization.id)
        )
        or 0
    )
    pending = int(
        db.scalar(
            select(func.count(OrganizationInvitation.id)).where(
                OrganizationInvitation.organization_id == organization.id,
                OrganizationInvitation.accepted_at.is_(None),
                OrganizationInvitation.revoked_at.is_(None),
                OrganizationInvitation.expires_at > utcnow(),
                OrganizationInvitation.email != invited_email,
            )
        )
        or 0
    )
    if members + pending + 1 > limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "resource": "members",
                "current": members,
                "pending_invitations": pending,
                "limit": limit,
                "plan": organization.plan,
            },
        )


def create_or_refresh_invitation(
    db: Session,
    *,
    organization: Organization,
    invited_by_user_id: str,
    email: str,
    role: Role,
    notify_incidents: bool,
) -> tuple[OrganizationInvitation, str, bool]:
    normalized_email = email.strip().lower()
    existing_member = db.scalar(
        select(Membership.id)
        .join(User, User.id == Membership.user_id)
        .where(
            Membership.organization_id == organization.id,
            User.email == normalized_email,
        )
    )
    if existing_member:
        raise HTTPException(status_code=409, detail="Bu kullanıcı zaten kuruluş üyesi.")

    ensure_invitation_capacity(db, organization, invited_email=normalized_email)
    raw_token = create_one_time_token()
    invitation = db.scalar(
        select(OrganizationInvitation)
        .where(
            OrganizationInvitation.organization_id == organization.id,
            OrganizationInvitation.email == normalized_email,
            OrganizationInvitation.accepted_at.is_(None),
        )
        .order_by(OrganizationInvitation.created_at.desc())
    )
    refreshed = invitation is not None
    if invitation is None:
        invitation = OrganizationInvitation(
            organization_id=organization.id,
            email=normalized_email,
        )
        db.add(invitation)
    invitation.role = role
    invitation.notify_incidents = notify_incidents
    invitation.token_hash = hash_one_time_token(raw_token)
    invitation.expires_at = utcnow() + timedelta(seconds=settings.invitation_ttl_seconds)
    invitation.accepted_at = None
    invitation.revoked_at = None
    invitation.invited_by_user_id = invited_by_user_id
    invitation.updated_at = utcnow()
    db.flush()

    organization_invitation_email(
        db,
        organization_id=organization.id,
        email=normalized_email,
        organization_name=organization.name,
        role=role.value,
        token=raw_token,
        expires_seconds=settings.invitation_ttl_seconds,
    )
    return invitation, raw_token, refreshed


def accept_invitation(
    db: Session,
    *,
    raw_token: str,
    password: str | None,
    request: Request,
) -> tuple[User, Membership, Organization, str, bool]:
    invitation = invitation_by_token(db, raw_token, lock=True)
    organization = db.get(Organization, invitation.organization_id)
    if not organization or not organization.is_active or organization.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Davet edilen kuruluş etkin değil.")
    user = db.scalar(select(User).where(User.email == invitation.email))
    created_user = False
    if user is None:
        if not password:
            raise HTTPException(
                status_code=422,
                detail={"code": "PASSWORD_REQUIRED", "message": "Yeni hesap için parola zorunludur."},
            )
        user = User(
            email=invitation.email,
            password_hash=hash_password(password),
            is_active=True,
            is_email_verified=True,
            email_verified_at=utcnow(),
        )
        db.add(user)
        db.flush()
        created_user = True
    elif not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Bu e-posta için etkin kullanıcı hesabı bulunmuyor.")
    else:
        user.is_email_verified = True
        user.email_verified_at = user.email_verified_at or utcnow()

    membership = db.scalar(
        select(Membership).where(
            Membership.organization_id == organization.id,
            Membership.user_id == user.id,
        )
    )
    if membership is None:
        membership = Membership(
            organization_id=organization.id,
            user_id=user.id,
            role=invitation.role,
            notify_incidents=invitation.notify_incidents,
        )
        db.add(membership)
    invitation.accepted_at = utcnow()
    invitation.updated_at = utcnow()
    db.flush()
    access_token, _session = create_session(db, user, request)
    return user, membership, organization, access_token, created_user


def revoke_invitation(db: Session, invitation: OrganizationInvitation) -> None:
    if invitation.accepted_at is not None:
        raise HTTPException(status_code=409, detail="Kabul edilmiş davet iptal edilemez.")
    invitation.revoked_at = utcnow()
    invitation.updated_at = utcnow()
    db.flush()
