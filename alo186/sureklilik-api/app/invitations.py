from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .audit import write_audit
from .auth_service import create_session
from .config import settings
from .deps import OrgContext, get_current_user, get_db, require_roles
from .models import (
    Membership,
    Organization,
    OrganizationInvitation,
    Role,
    User,
    utcnow,
)
from .notifications import invitation_email
from .plans import ensure_subscription_writable, plan_limits
from .rate_limit import enforce_auth_rate
from .schemas import AuthResponse, MemberOut, OrganizationOut, UserOut
from .security import create_one_time_token, hash_one_time_token, hash_password

router = APIRouter(prefix="/api/v1", tags=["invitations"])


class InvitationCreate(BaseModel):
    email: EmailStr
    role: Role = Role.viewer
    notify_incidents: bool = True


class InvitationAcceptNew(BaseModel):
    token: str = Field(min_length=20, max_length=300)
    password: str = Field(min_length=10, max_length=200)


class InvitationToken(BaseModel):
    token: str = Field(min_length=20, max_length=300)


class InvitationOut(BaseModel):
    id: str
    organization_id: str
    email: EmailStr
    role: Role
    notify_incidents: bool
    status: str
    expires_at: datetime
    created_at: datetime
    accepted_at: datetime | None = None
    revoked_at: datetime | None = None
    resend_count: int
    test_token: str | None = None


class InvitationPreview(BaseModel):
    organization_id: str
    organization_name: str
    email_masked: str
    role: Role
    notify_incidents: bool
    expires_at: datetime
    existing_account: bool


def _aware(value: datetime | None) -> datetime | None:
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _status(invitation: OrganizationInvitation) -> str:
    if invitation.accepted_at is not None:
        return "accepted"
    if invitation.revoked_at is not None:
        return "revoked"
    if _aware(invitation.expires_at) < utcnow():
        return "expired"
    return "pending"


def _out(invitation: OrganizationInvitation, *, test_token: str | None = None) -> InvitationOut:
    return InvitationOut(
        id=invitation.id,
        organization_id=invitation.organization_id,
        email=invitation.email,
        role=invitation.role,
        notify_incidents=invitation.notify_incidents,
        status=_status(invitation),
        expires_at=invitation.expires_at,
        created_at=invitation.created_at,
        accepted_at=invitation.accepted_at,
        revoked_at=invitation.revoked_at,
        resend_count=invitation.resend_count,
        test_token=test_token if settings.expose_test_tokens else None,
    )


def _mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        masked = local[0] + "*" if local else "*"
    else:
        masked = local[0] + "*" * (len(local) - 2) + local[-1]
    return f"{masked}@{domain}"


def _valid_invitation(db: Session, raw_token: str, *, lock: bool = False) -> OrganizationInvitation:
    query = select(OrganizationInvitation).where(
        OrganizationInvitation.token_hash == hash_one_time_token(raw_token)
    )
    if lock and db.bind and db.bind.dialect.name == "postgresql":
        query = query.with_for_update()
    invitation = db.scalar(query)
    if (
        not invitation
        or invitation.accepted_at is not None
        or invitation.revoked_at is not None
        or _aware(invitation.expires_at) < utcnow()
    ):
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş davet bağlantısı.")
    organization = db.get(Organization, invitation.organization_id)
    if not organization or not organization.is_active or organization.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş davet bağlantısı.")
    return invitation


def _active_invitation_count(db: Session, organization_id: str, *, exclude_id: str | None = None) -> int:
    query = select(func.count(OrganizationInvitation.id)).where(
        OrganizationInvitation.organization_id == organization_id,
        OrganizationInvitation.accepted_at.is_(None),
        OrganizationInvitation.revoked_at.is_(None),
        OrganizationInvitation.expires_at > utcnow(),
    )
    if exclude_id:
        query = query.where(OrganizationInvitation.id != exclude_id)
    return int(db.scalar(query) or 0)


def _member_count(db: Session, organization_id: str) -> int:
    return int(
        db.scalar(select(func.count(Membership.id)).where(Membership.organization_id == organization_id)) or 0
    )


def _ensure_invitation_capacity(
    db: Session,
    organization: Organization,
    *,
    exclude_invitation_id: str | None = None,
) -> None:
    ensure_subscription_writable(organization)
    limit = plan_limits(organization).get("members")
    if limit is None:
        return
    members = _member_count(db, organization.id)
    pending = _active_invitation_count(db, organization.id, exclude_id=exclude_invitation_id)
    if members + pending + 1 > limit:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PLAN_LIMIT_REACHED",
                "resource": "members",
                "current_members": members,
                "pending_invitations": pending,
                "limit": limit,
                "plan": organization.plan,
            },
        )


def _issue_token(invitation: OrganizationInvitation) -> str:
    raw = create_one_time_token()
    invitation.token_hash = hash_one_time_token(raw)
    invitation.expires_at = utcnow() + timedelta(seconds=settings.invitation_ttl_seconds)
    invitation.updated_at = utcnow()
    return raw


def _queue_invitation(db: Session, invitation: OrganizationInvitation, organization: Organization, raw: str) -> None:
    invitation_email(
        db,
        organization_id=organization.id,
        email=invitation.email,
        organization_name=organization.name,
        role=invitation.role.value,
        notify_incidents=invitation.notify_incidents,
        token=raw,
        expires_seconds=settings.invitation_ttl_seconds,
    )


@router.get("/organizations/{organization_id}/invitations", response_model=list[InvitationOut])
def list_invitations(
    organization_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    invitations = db.scalars(
        select(OrganizationInvitation)
        .where(OrganizationInvitation.organization_id == organization_id)
        .order_by(OrganizationInvitation.created_at.desc())
        .limit(200)
    ).all()
    return [_out(item) for item in invitations]


@router.post(
    "/organizations/{organization_id}/invitations",
    response_model=InvitationOut,
    status_code=status.HTTP_201_CREATED,
)
def create_invitation(
    organization_id: str,
    payload: InvitationCreate,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    organization_query = select(Organization).where(Organization.id == organization_id)
    if db.bind and db.bind.dialect.name == "postgresql":
        organization_query = organization_query.with_for_update()
    organization = db.scalar(organization_query)
    if not organization:
        raise HTTPException(status_code=404, detail="Kuruluş bulunamadı.")
    email = payload.email.lower()
    user = db.scalar(select(User).where(User.email == email))
    if user and db.scalar(
        select(Membership.id).where(
            Membership.user_id == user.id,
            Membership.organization_id == organization_id,
        )
    ):
        raise HTTPException(status_code=409, detail="Kullanıcı zaten bu kuruluşun üyesi.")

    active = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.organization_id == organization_id,
            OrganizationInvitation.email == email,
            OrganizationInvitation.accepted_at.is_(None),
            OrganizationInvitation.revoked_at.is_(None),
            OrganizationInvitation.expires_at > utcnow(),
        )
    )
    if active:
        active.role = payload.role
        active.notify_incidents = payload.notify_incidents
        active.resend_count += 1
        raw = _issue_token(active)
        invitation = active
        action = "invitation.renewed"
        response_status = status.HTTP_200_OK
    else:
        _ensure_invitation_capacity(db, organization)
        invitation = OrganizationInvitation(
            organization_id=organization_id,
            email=email,
            role=payload.role,
            notify_incidents=payload.notify_incidents,
            token_hash="pending",
            expires_at=utcnow(),
            invited_by_user_id=context.user.id,
        )
        raw = _issue_token(invitation)
        db.add(invitation)
        action = "invitation.created"
        response_status = status.HTTP_201_CREATED
    db.flush()
    _queue_invitation(db, invitation, organization, raw)
    write_audit(
        db,
        organization_id=organization_id,
        user_id=context.user.id,
        action=action,
        entity_type="organization_invitation",
        entity_id=invitation.id,
        details={
            "email": email,
            "role": invitation.role.value,
            "notify_incidents": invitation.notify_incidents,
            "response_status": response_status,
        },
    )
    db.commit()
    return _out(invitation, test_token=raw)


@router.post(
    "/organizations/{organization_id}/invitations/{invitation_id}/resend",
    response_model=InvitationOut,
)
def resend_invitation(
    organization_id: str,
    invitation_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    invitation = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.id == invitation_id,
            OrganizationInvitation.organization_id == organization_id,
        )
    )
    if not invitation or invitation.accepted_at is not None or invitation.revoked_at is not None:
        raise HTTPException(status_code=404, detail="Aktif davet bulunamadı.")
    _ensure_invitation_capacity(db, context.organization, exclude_invitation_id=invitation.id)
    invitation.resend_count += 1
    raw = _issue_token(invitation)
    _queue_invitation(db, invitation, context.organization, raw)
    write_audit(
        db,
        organization_id=organization_id,
        user_id=context.user.id,
        action="invitation.resent",
        entity_type="organization_invitation",
        entity_id=invitation.id,
        details={"email": invitation.email, "resend_count": invitation.resend_count},
    )
    db.commit()
    return _out(invitation, test_token=raw)


@router.delete(
    "/organizations/{organization_id}/invitations/{invitation_id}",
    response_model=InvitationOut,
)
def revoke_invitation(
    organization_id: str,
    invitation_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    invitation = db.scalar(
        select(OrganizationInvitation).where(
            OrganizationInvitation.id == invitation_id,
            OrganizationInvitation.organization_id == organization_id,
        )
    )
    if not invitation:
        raise HTTPException(status_code=404, detail="Davet bulunamadı.")
    if invitation.accepted_at is not None:
        raise HTTPException(status_code=409, detail="Kabul edilmiş davet iptal edilemez.")
    if invitation.revoked_at is None:
        invitation.revoked_at = utcnow()
        invitation.updated_at = utcnow()
        write_audit(
            db,
            organization_id=organization_id,
            user_id=context.user.id,
            action="invitation.revoked",
            entity_type="organization_invitation",
            entity_id=invitation.id,
            details={"email": invitation.email},
        )
        db.commit()
    return _out(invitation)


@router.post("/invitations/preview", response_model=InvitationPreview)
def preview_invitation(payload: InvitationToken, db: Session = Depends(get_db)) -> InvitationPreview:
    invitation = _valid_invitation(db, payload.token)
    organization = db.get(Organization, invitation.organization_id)
    existing = bool(db.scalar(select(User.id).where(User.email == invitation.email)))
    return InvitationPreview(
        organization_id=organization.id,
        organization_name=organization.name,
        email_masked=_mask_email(invitation.email),
        role=invitation.role,
        notify_incidents=invitation.notify_incidents,
        expires_at=invitation.expires_at,
        existing_account=existing,
    )


@router.post("/invitations/accept-new", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def accept_invitation_new(
    payload: InvitationAcceptNew,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    invitation = _valid_invitation(db, payload.token, lock=True)
    enforce_auth_rate(request, invitation.email)
    if db.scalar(select(User.id).where(User.email == invitation.email)):
        raise HTTPException(
            status_code=409,
            detail={"code": "EXISTING_ACCOUNT", "message": "Bu e-posta için mevcut hesapla kabul endpointini kullanın."},
        )
    organization = db.get(Organization, invitation.organization_id)
    user = User(
        email=invitation.email,
        password_hash=hash_password(payload.password),
        is_email_verified=True,
        email_verified_at=utcnow(),
    )
    membership = Membership(
        user=user,
        organization_id=organization.id,
        role=invitation.role,
        notify_incidents=invitation.notify_incidents,
    )
    db.add_all([user, membership])
    db.flush()
    invitation.accepted_at = utcnow()
    invitation.accepted_by_user_id = user.id
    invitation.updated_at = utcnow()
    access_token, _session = create_session(db, user, request)
    write_audit(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="invitation.accepted",
        entity_type="organization_invitation",
        entity_id=invitation.id,
        details={"new_user": True, "role": membership.role.value},
    )
    db.commit()
    return AuthResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(organization),
        email_verification_required=False,
    )


@router.post("/invitations/accept-existing", response_model=MemberOut)
def accept_invitation_existing(
    payload: InvitationToken,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemberOut:
    invitation = _valid_invitation(db, payload.token, lock=True)
    if invitation.email != user.email.lower():
        raise HTTPException(status_code=403, detail="Davet e-postası oturum hesabıyla eşleşmiyor.")
    organization = db.get(Organization, invitation.organization_id)
    membership = db.scalar(
        select(Membership).where(
            Membership.user_id == user.id,
            Membership.organization_id == organization.id,
        )
    )
    if not membership:
        membership = Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=invitation.role,
            notify_incidents=invitation.notify_incidents,
        )
        db.add(membership)
        db.flush()
    invitation.accepted_at = utcnow()
    invitation.accepted_by_user_id = user.id
    invitation.updated_at = utcnow()
    if not user.is_email_verified:
        user.is_email_verified = True
        user.email_verified_at = utcnow()
    write_audit(
        db,
        organization_id=organization.id,
        user_id=user.id,
        action="invitation.accepted",
        entity_type="organization_invitation",
        entity_id=invitation.id,
        details={"new_user": False, "role": membership.role.value},
    )
    db.commit()
    return MemberOut(
        user_id=user.id,
        email=user.email,
        role=membership.role,
        notify_incidents=membership.notify_incidents,
    )
