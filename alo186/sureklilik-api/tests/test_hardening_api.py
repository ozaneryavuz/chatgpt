from __future__ import annotations

from sqlalchemy import select

from app.db import SessionLocal
from app.models import EmailOutbox, User
from app.notifications import process_outbox, read_payload
from app.security import totp_code


def register(client, email: str, organization_name: str, password: str = "Guvenli-Parola-2026"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "organization_name": organization_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Organization-ID": auth["organization"]["id"],
    }


def test_session_logout_and_password_reset(client):
    auth = register(client, "session-user@example.com", "Session Tesisi")
    auth_headers = headers(auth)

    sessions = client.get("/api/v1/auth/sessions", headers=auth_headers)
    assert sessions.status_code == 200, sessions.text
    assert len(sessions.json()) == 1

    reset = client.post(
        "/api/v1/auth/password-reset/request",
        json={"email": "session-user@example.com"},
    )
    assert reset.status_code == 202, reset.text
    token = reset.json()["test_token"]
    assert token

    confirm = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={"token": token, "new_password": "Yeni-Guvenli-Parola-2026"},
    )
    assert confirm.status_code == 200, confirm.text
    assert client.get("/api/v1/auth/me", headers=auth_headers).status_code == 401

    old_login = client.post(
        "/api/v1/auth/login",
        json={"email": "session-user@example.com", "password": "Guvenli-Parola-2026"},
    )
    assert old_login.status_code == 401
    new_login = client.post(
        "/api/v1/auth/login",
        json={"email": "session-user@example.com", "password": "Yeni-Guvenli-Parola-2026"},
    )
    assert new_login.status_code == 200, new_login.text

    logout_headers = headers(new_login.json())
    assert client.post("/api/v1/auth/logout", headers=logout_headers).status_code == 200
    assert client.get("/api/v1/auth/me", headers=logout_headers).status_code == 401


def test_email_verification_and_outbox_processing(client):
    auth = register(client, "verify-user@example.com", "Doğrulama Tesisi")
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "verify-user@example.com"))
        assert user is not None
        user.is_email_verified = False
        user.email_verified_at = None
        db.commit()

    requested = client.post(
        "/api/v1/auth/email-verification/request",
        json={"email": "verify-user@example.com"},
    )
    assert requested.status_code == 202, requested.text
    token = requested.json()["test_token"]
    assert token

    confirmed = client.post(
        "/api/v1/auth/email-verification/confirm",
        json={"token": token},
    )
    assert confirmed.status_code == 200, confirmed.text

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "verify-user@example.com"))
        assert user and user.is_email_verified
        message = db.scalar(
            select(EmailOutbox)
            .where(EmailOutbox.user_id == user.id, EmailOutbox.template == "verify_email")
            .order_by(EmailOutbox.created_at.desc())
        )
        assert message is not None
        assert token not in message.payload_json
        payload = read_payload(message)
        assert payload["token"] == token
        result = process_outbox(db, limit=20)
        assert result["sent"] >= 1
        db.refresh(message)
        assert message.status == "sent"


def test_totp_mfa_and_single_use_recovery_code(client):
    auth = register(client, "mfa-user@example.com", "MFA Tesisi")
    auth_headers = headers(auth)

    setup = client.post("/api/v1/auth/mfa/setup", headers=auth_headers)
    assert setup.status_code == 200, setup.text
    secret = setup.json()["secret"]
    assert setup.json()["provisioning_uri"].startswith("otpauth://totp/")

    enabled = client.post(
        "/api/v1/auth/mfa/enable",
        headers=auth_headers,
        json={"code": totp_code(secret)},
    )
    assert enabled.status_code == 200, enabled.text
    recovery_codes = enabled.json()["recovery_codes"]
    assert len(recovery_codes) == 8

    missing = client.post(
        "/api/v1/auth/login",
        json={"email": "mfa-user@example.com", "password": "Guvenli-Parola-2026"},
    )
    assert missing.status_code == 401
    assert missing.json()["detail"]["code"] == "MFA_REQUIRED"

    totp_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "mfa-user@example.com",
            "password": "Guvenli-Parola-2026",
            "mfa_code": totp_code(secret),
        },
    )
    assert totp_login.status_code == 200, totp_login.text

    recovery_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "mfa-user@example.com",
            "password": "Guvenli-Parola-2026",
            "mfa_code": recovery_codes[0],
        },
    )
    assert recovery_login.status_code == 200, recovery_login.text
    repeated = client.post(
        "/api/v1/auth/login",
        json={
            "email": "mfa-user@example.com",
            "password": "Guvenli-Parola-2026",
            "mfa_code": recovery_codes[0],
        },
    )
    assert repeated.status_code == 401


def test_account_lock_metrics_and_security_headers(client):
    register(client, "locked-user@example.com", "Kilit Tesisi")
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "locked-user@example.com", "password": "Yanlis-Parola-2026"},
        )
        assert response.status_code == 401
    locked = client.post(
        "/api/v1/auth/login",
        json={"email": "locked-user@example.com", "password": "Guvenli-Parola-2026"},
    )
    assert locked.status_code == 423

    health = client.get("/health/ready")
    assert health.status_code == 200
    assert health.headers["x-content-type-options"] == "nosniff"
    assert health.headers["x-frame-options"] == "DENY"
    assert "x-request-id" in health.headers

    assert client.get("/metrics").status_code == 403
    metrics = client.get("/metrics", headers={"X-Metrics-Token": "test-metrics-token"})
    assert metrics.status_code == 200
    assert "alo186_http_requests_total" in metrics.text
