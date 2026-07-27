from __future__ import annotations

import json
import logging
import smtplib
from datetime import timedelta
from email.message import EmailMessage

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import EmailOutbox, utcnow
from .security import decrypt_secret, encrypt_secret

logger = logging.getLogger(__name__)


def queue_email(
    db: Session,
    *,
    to_email: str,
    template: str,
    subject: str,
    payload: dict[str, object],
    user_id: str | None = None,
    organization_id: str | None = None,
) -> EmailOutbox:
    message = EmailOutbox(
        user_id=user_id,
        organization_id=organization_id,
        to_email=to_email.lower(),
        template=template,
        subject=subject,
        payload_json=encrypt_secret(json.dumps(payload, ensure_ascii=False, separators=(",", ":"))),
        status="pending",
    )
    db.add(message)
    db.flush()
    return message


def read_payload(message: EmailOutbox) -> dict[str, object]:
    return json.loads(decrypt_secret(message.payload_json))


def verification_email(db: Session, *, user_id: str, email: str, token: str) -> EmailOutbox:
    return queue_email(
        db,
        user_id=user_id,
        to_email=email,
        template="verify_email",
        subject="ALO186 e-posta adresinizi doğrulayın",
        payload={
            "email": email,
            "url": f"{settings.public_base_url}/verify-email?token={token}",
            "api_url": f"{settings.public_base_url}/api/v1/auth/email-verification/confirm",
            "token": token,
            "expires_seconds": settings.email_token_ttl_seconds,
        },
    )


def password_reset_email(db: Session, *, user_id: str, email: str, token: str) -> EmailOutbox:
    return queue_email(
        db,
        user_id=user_id,
        to_email=email,
        template="password_reset",
        subject="ALO186 parola sıfırlama bağlantısı",
        payload={
            "email": email,
            "url": f"{settings.public_base_url}/reset-password?token={token}",
            "api_url": f"{settings.public_base_url}/api/v1/auth/password-reset/confirm",
            "token": token,
            "expires_seconds": settings.password_reset_ttl_seconds,
        },
    )


def organization_invitation_email(
    db: Session,
    *,
    organization_id: str,
    email: str,
    organization_name: str,
    role: str,
    token: str,
    expires_seconds: int,
) -> EmailOutbox:
    return queue_email(
        db,
        organization_id=organization_id,
        to_email=email,
        template="organization_invitation",
        subject=f"{organization_name} sizi ALO186 ekibine davet etti",
        payload={
            "email": email,
            "organization_name": organization_name,
            "role": role,
            "url": f"{settings.public_base_url}/davet?token={token}",
            "api_preview_url": f"{settings.public_base_url}/api/v1/invitations/{token}",
            "api_accept_url": f"{settings.public_base_url}/api/v1/invitations/accept",
            "token": token,
            "expires_seconds": expires_seconds,
        },
    )


def incident_email(
    db: Session,
    *,
    user_id: str,
    organization_id: str,
    email: str,
    organization_name: str,
    incident_id: str,
    action: str,
    summary: str,
) -> EmailOutbox:
    return queue_email(
        db,
        user_id=user_id,
        organization_id=organization_id,
        to_email=email,
        template="incident_event",
        subject=f"ALO186 süreklilik olayı: {action}",
        payload={
            "organization_name": organization_name,
            "incident_id": incident_id,
            "action": action,
            "summary": summary,
        },
    )


def render_message(message: EmailOutbox) -> tuple[str, str]:
    payload = read_payload(message)
    if message.template == "verify_email":
        text = (
            "ALO186 e-posta doğrulama\n\n"
            f"Doğrulama bağlantısı: {payload['url']}\n\n"
            f"Bağlantı yaklaşık {int(payload['expires_seconds']) // 3600} saat geçerlidir."
        )
    elif message.template == "password_reset":
        text = (
            "ALO186 parola sıfırlama\n\n"
            f"Parola sıfırlama bağlantısı: {payload['url']}\n\n"
            "Bu talebi siz oluşturmadıysanız bağlantıyı kullanmayın."
        )
    elif message.template == "organization_invitation":
        days = max(1, int(payload["expires_seconds"]) // 86_400)
        text = (
            "ALO186 ekip daveti\n\n"
            f"Kuruluş: {payload['organization_name']}\n"
            f"Rol: {payload['role']}\n"
            f"Davet edilen e-posta: {payload['email']}\n\n"
            f"Daveti kabul et: {payload['url']}\n\n"
            f"Bağlantı yaklaşık {days} gün geçerlidir. Bu daveti beklemiyorsanız bağlantıyı kullanmayın."
        )
    elif message.template == "incident_event":
        text = (
            f"Kuruluş: {payload['organization_name']}\n"
            f"Olay: {payload['incident_id']}\n"
            f"İşlem: {payload['action']}\n\n"
            f"{payload['summary']}"
        )
    else:
        text = json.dumps(payload, ensure_ascii=False, indent=2)
    html = "<br>".join(_escape_html(text).splitlines())
    return text, f"<html><body><p>{html}</p></body></html>"


def _escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _send_smtp(message: EmailOutbox, text: str, html: str) -> None:
    if not settings.smtp_host:
        raise RuntimeError("SMTP host tanımlı değil.")
    email = EmailMessage()
    email["Subject"] = message.subject
    email["From"] = settings.smtp_from_email
    email["To"] = message.to_email
    email.set_content(text)
    email.add_alternative(html, subtype="html")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_use_tls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or "")
        smtp.send_message(email)


def send_message(message: EmailOutbox) -> None:
    text, html = render_message(message)
    if settings.email_backend == "console":
        logger.info(
            "transactional_email_console",
            extra={
                "user_id": message.user_id,
                "organization_id": message.organization_id,
                "path": message.template,
            },
        )
        logger.info("email_to=%s subject=%s\n%s", message.to_email, message.subject, text)
        return
    if settings.email_backend != "smtp":
        raise RuntimeError(f"Bilinmeyen e-posta backend: {settings.email_backend}")
    _send_smtp(message, text, html)


def process_outbox(db: Session, *, limit: int = 50) -> dict[str, int]:
    now = utcnow()
    query = (
        select(EmailOutbox)
        .where(
            EmailOutbox.status.in_(["pending", "retry"]),
            EmailOutbox.available_at <= now,
        )
        .order_by(EmailOutbox.created_at)
        .limit(max(1, min(limit, 200)))
    )
    if db.bind and db.bind.dialect.name == "postgresql":
        query = query.with_for_update(skip_locked=True)
    messages = list(db.scalars(query).all())
    sent = failed = 0
    for message in messages:
        try:
            send_message(message)
            message.status = "sent"
            message.sent_at = utcnow()
            message.last_error = None
            sent += 1
        except Exception as exc:  # pragma: no cover - SMTP entegrasyonunda çalışır
            message.attempts += 1
            message.last_error = str(exc)[:2_000]
            if message.attempts >= 5:
                message.status = "failed"
                failed += 1
            else:
                message.status = "retry"
                message.available_at = utcnow() + timedelta(minutes=min(60, 2**message.attempts))
            logger.exception("E-posta gönderilemedi", extra={"user_id": message.user_id})
    db.commit()
    return {"processed": len(messages), "sent": sent, "failed": failed}
