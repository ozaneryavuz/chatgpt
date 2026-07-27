from __future__ import annotations

from dataclasses import dataclass
from typing import Generator

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import SessionLocal
from .models import Membership, Role, User
from .security import decode_access_token

bearer = HTTPBearer(auto_error=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Oturum gerekli.")
    try:
        user_id = decode_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Kullanıcı bulunamadı.")
    return user


@dataclass(frozen=True)
class OrgContext:
    organization_id: str
    membership: Membership
    user: User


def get_org_context(
    organization_header: str = Header(alias="X-Organization-ID"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OrgContext:
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
    return OrgContext(organization_id=organization_header, membership=membership, user=user)


def require_roles(*roles: Role):
    def dependency(context: OrgContext = Depends(get_org_context)) -> OrgContext:
        if context.membership.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bu işlem için yetkiniz yok.",
            )
        return context

    return dependency
