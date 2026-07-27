from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .audit import write_audit
from .config import settings
from .deps import OrgContext, get_db, require_roles
from .invitation_schemas import (
    InvitationAcceptRequest,
    InvitationAcceptResponse,
    InvitationCreate,
    InvitationOut,
    InvitationPreview,
)
from .invitations import (
    accept_invitation,
    create_or_refresh_invitation,
    invitation_by_token,
    invitation_status,
    revoke_invitation,
)
from .models import OrganizationInvitation, Role, User
from .rate_limit import enforce_auth_rate
from .schemas import OrganizationOut, UserOut

router = APIRouter(tags=["invitations"])


def invitation_out(invitation: OrganizationInvitation, *, test_token: str | None = None) -> InvitationOut:
    return InvitationOut(
        id=invitation.id,
        organization_id=invitation.organization_id,
        email=invitation.email,
        role=invitation.role,
        notify_incidents=invitation.notify_incidents,
        expires_at=invitation.expires_at,
        accepted_at=invitation.accepted_at,
        revoked_at=invitation.revoked_at,
        status=invitation_status(invitation),
        created_at=invitation.created_at,
        test_token=test_token if settings.expose_test_tokens else None,
    )


@router.get(
    "/api/v1/organizations/{organization_id}/invitations",
    response_model=list[InvitationOut],
)
def list_invitations(
    organization_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
):
    if context.organization_id != organization_id:
        raise HTTPException(status_code=403, detail="Kuruluş başlığı eşleşmiyor.")
    rows = db.scalars(
        select(OrganizationInvitation)
        .where(OrganizationInvitation.organization_id == organization_id)
        .order_by(OrganizationInvitation.created_at.desc())
        .limit(200)
    ).all()
    return [invitation_out(item) for item in rows]


@router.post(
    "/api/v1/organizations/{organization_id}/invitations",
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
    invitation, raw_token, refreshed = create_or_refresh_invitation(
        db,
        organization=context.organization,
        invited_by_user_id=context.user.id,
        email=str(payload.email),
        role=payload.role,
        notify_incidents=payload.notify_incidents,
    )
    write_audit(
        db,
        organization_id=organization_id,
        user_id=context.user.id,
        action="invitation.refreshed" if refreshed else "invitation.created",
        entity_type="organization_invitation",
        entity_id=invitation.id,
        details={
            "email": invitation.email,
            "role": invitation.role.value,
            "notify_incidents": invitation.notify_incidents,
        },
    )
    db.commit()
    db.refresh(invitation)
    return invitation_out(invitation, test_token=raw_token)


@router.delete(
    "/api/v1/organizations/{organization_id}/invitations/{invitation_id}",
    response_model=InvitationOut,
)
def cancel_invitation(
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
    revoke_invitation(db, invitation)
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
    return invitation_out(invitation)


@router.get("/api/v1/invitations/{token}", response_model=InvitationPreview)
def preview_invitation(token: str, request: Request, db: Session = Depends(get_db)):
    enforce_auth_rate(request, token[:16])
    invitation = invitation_by_token(db, token)
    organization = invitation.organization or db.get(__import__("app.models", fromlist=["Organization"]).Organization, invitation.organization_id)
    if not organization:
        raise HTTPException(status_code=400, detail="Davet edilen kuruluş bulunamadı.")
    existing_user = db.scalar(select(User.id).where(User.email == invitation.email)) is not None
    return InvitationPreview(
        organization_name=organization.name,
        email=invitation.email,
        role=invitation.role,
        notify_incidents=invitation.notify_incidents,
        expires_at=invitation.expires_at,
        existing_user=existing_user,
    )


@router.post(
    "/api/v1/invitations/accept",
    response_model=InvitationAcceptResponse,
    status_code=status.HTTP_201_CREATED,
)
def accept_organization_invitation(
    payload: InvitationAcceptRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    enforce_auth_rate(request, payload.token[:16])
    try:
        user, membership, organization, access_token, created_user = accept_invitation(
            db,
            raw_token=payload.token,
            password=payload.password,
            request=request,
        )
        invitation = db.scalar(
            select(OrganizationInvitation).where(
                OrganizationInvitation.organization_id == organization.id,
                OrganizationInvitation.email == user.email,
                OrganizationInvitation.accepted_at.is_not(None),
            ).order_by(OrganizationInvitation.accepted_at.desc())
        )
        write_audit(
            db,
            organization_id=organization.id,
            user_id=user.id,
            action="invitation.accepted",
            entity_type="organization_invitation",
            entity_id=invitation.id if invitation else membership.id,
            details={
                "email": user.email,
                "role": membership.role.value,
                "created_user": created_user,
            },
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Davet kabulü eşzamanlı başka işlemle çakıştı.") from exc
    return InvitationAcceptResponse(
        access_token=access_token,
        user=UserOut.model_validate(user),
        organization=OrganizationOut.model_validate(organization),
        email_verification_required=False,
        created_user=created_user,
        invitation_id=invitation.id if invitation else membership.id,
    )
