from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Request, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .config import settings
from .models import AuthSession, AuthToken, User, new_id, utcnow
from .security import (
    consume_recovery_code,
    create_access_token,
    create_one_time_token,
    decrypt_secret,
    hash_client_value,
    hash_one_time_token,
    verify_totp,
)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def request_fingerprint(request: Request | None) -> tuple[str | None, str | None]:
    if request is None:
        return None, None
    if settings.trust_proxy_headers and request.headers.get("x-forwarded-for"):
        ip = request.headers["x-forwarded-for"].split(",", 1)[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")[:500]
    return hash_client_value(ip), hash_client_value(user_agent)


def create_session(db: Session, user: User, request: Request | None = None) -> tuple[str, AuthSession]:
    expires_at = utcnow() + timedelta(seconds=settings.token_ttl_seconds)
    ip_hash, user_agent_hash = request_fingerprint(request)
    session = AuthSession(
        id=new_id(),
        user_id=user.id,
        token_version=user.token_version,
        expires_at=expires_at,
        ip_hash=ip_hash,
        user_agent_hash=user_agent_hash,
    )
    db.add(session)
    db.flush()
    token = create_access_token(
        user.id,
        session_id=session.id,
        token_version=user.token_version,
        expires_at=expires_at,
    )
    return token, session


def revoke_session(db: Session, session_id: str) -> bool:
    session = db.get(AuthSession, session_id)
    if not session or session.revoked_at is not None:
        return False
    session.revoked_at = utcnow()
    db.flush()
    return True


def revoke_all_sessions(db: Session, user: User, *, except_session_id: str | None = None) -> int:
    query = update(AuthSession).where(
        AuthSession.user_id == user.id,
        AuthSession.revoked_at.is_(None),
    )
    if except_session_id:
        query = query.where(AuthSession.id != except_session_id)
    result = db.execute(query.values(revoked_at=utcnow()))
    user.token_version += 1
    db.flush()
    return int(result.rowcount or 0)


def issue_one_time_token(
    db: Session,
    *,
    user: User,
    purpose: str,
    ttl_seconds: int,
    request: Request | None = None,
) -> str:
    db.execute(
        update(AuthToken)
        .where(
            AuthToken.user_id == user.id,
            AuthToken.purpose == purpose,
            AuthToken.consumed_at.is_(None),
        )
        .values(consumed_at=utcnow())
    )
    raw = create_one_time_token()
    ip_hash, _ = request_fingerprint(request)
    db.add(
        AuthToken(
            user_id=user.id,
            purpose=purpose,
            token_hash=hash_one_time_token(raw),
            expires_at=utcnow() + timedelta(seconds=ttl_seconds),
            request_ip_hash=ip_hash,
        )
    )
    db.flush()
    return raw


def consume_one_time_token(db: Session, *, raw_token: str, purpose: str) -> User:
    token_hash = hash_one_time_token(raw_token)
    token = db.scalar(
        select(AuthToken).where(
            AuthToken.token_hash == token_hash,
            AuthToken.purpose == purpose,
        )
    )
    if not token or token.consumed_at is not None or _aware(token.expires_at) < utcnow():
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş bağlantı.")
    user = db.get(User, token.user_id)
    if not user or user.deleted_at is not None:
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş bağlantı.")
    token.consumed_at = utcnow()
    db.flush()
    return user


def account_is_locked(user: User) -> bool:
    locked_until = _aware(user.locked_until)
    if not locked_until:
        return False
    if locked_until <= utcnow():
        user.locked_until = None
        user.failed_login_count = 0
        return False
    return True


def register_failed_login(db: Session, user: User | None) -> None:
    if not user:
        return
    user.failed_login_count += 1
    if user.failed_login_count >= settings.account_lock_threshold:
        user.locked_until = utcnow() + timedelta(seconds=settings.account_lock_seconds)
        user.failed_login_count = 0
    db.flush()


def register_successful_login(db: Session, user: User) -> None:
    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = utcnow()
    db.flush()


def verify_user_mfa(user: User, code: str | None) -> None:
    if not user.mfa_enabled:
        return
    if not code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MFA_REQUIRED", "message": "Çok faktörlü doğrulama kodu gerekli."},
        )
    if user.mfa_secret_ciphertext:
        secret = decrypt_secret(user.mfa_secret_ciphertext)
        if verify_totp(code, secret):
            return
    valid_recovery, remaining = consume_recovery_code(code, user.mfa_recovery_codes_json)
    if valid_recovery:
        user.mfa_recovery_codes_json = remaining
        return
    raise HTTPException(status_code=401, detail="MFA kodu veya kurtarma kodu geçersiz.")


def recovery_code_count(user: User) -> int:
    if not user.mfa_recovery_codes_json:
        return 0
    try:
        return len(json.loads(user.mfa_recovery_codes_json))
    except json.JSONDecodeError:
        return 0
