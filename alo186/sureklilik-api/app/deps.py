from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta, timezone
from typing import Generator

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import SessionLocal
from .models import AuthSession, Membership, Organization, Role, User, utcnow
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _aware(value):
    if value is not None and value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum gerekli.")
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    user_id = str(payload["sub"])
    session_id = str(payload["jti"])
    token_version = int(payload.get("ver", 0))
    user = db.get(User, user_id)
    if not user or not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı.")
    if user.token_version != token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum iptal edildi.")
    session = db.scalar(
        select(AuthSession).where(
            AuthSession.id == session_id,
            AuthSession.user_id == user.id,
            AuthSession.revoked_at.is_(None),
        )
    )
    if not session or _aware(session.expires_at) < utcnow() or session.token_version != user.token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum iptal edildi veya süresi doldu.")
    if _aware(session.last_seen_at) < utcnow() - timedelta(minutes=5):
        session.last_seen_at = utcnow()
        db.commit()
    request.state.auth_session_id = session.id
    request.state.user_id = user.id
    return user


@dataclass(frozen=True)
class OrgContext:
    organization_id: str
    membership: Membership
    organization: Organization
    user: User


def get_org_context(
    organization_header: str = Header(alias="X-Organization-ID"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgContext:
    if settings.email_verification_required and not user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "EMAIL_VERIFICATION_REQUIRED", "message": "E-posta doğrulaması gerekli."},
        )
    membership = db.scalar(
        select(Membership).where(
            Membership.organization_id == organization_header,
            Membership.user_id == user.id,
        )
    )
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu kuruluşa erişim yetkiniz yok.",
        )
    organization = db.get(Organization, organization_header)
    if not organization or not organization.is_active or organization.deleted_at is not None:
        raise HTTPException(status_code=403, detail="Kuruluş etkin değil.")
    if organization.deletion_requested_at is not None:
        raise HTTPException(status_code=423, detail="Kuruluş silme sürecinde; yazma ve erişim kısıtlandı.")
    return OrgContext(
        organization_id=organization_header,
        membership=membership,
        organization=organization,
        user=user,
    )


def require_roles(*roles: Role):
    def dependency(context: OrgContext = Depends(get_org_context)) -> OrgContext:
        if context.membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlem için yetkiniz yok.",
            )
        return context

    return dependency
