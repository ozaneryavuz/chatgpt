from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select

from app.db import SessionLocal
from app.models import EmailOutbox, Membership, OrganizationInvitation, Role, User, utcnow
from app.notifications import read_payload

PASSWORD = "Guvenli-Parola-2026"


def register(client, email: str, organization_name: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "organization_name": organization_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict, organization_id: str | None = None) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Organization-ID": organization_id or auth["organization"]["id"],
    }


def create_invite(client, admin: dict, email: str, role: str = "viewer", notify: bool = True):
    response = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=headers(admin),
        json={"email": email, "role": role, "notify_incidents": notify},
    )
    assert response.status_code == 201, response.text
    assert response.json()["test_token"]
    return response.json()


def test_new_user_invitation_acceptance_is_single_use(client):
    admin = register(client, "invite-admin-new@example.com", "Davet Yeni Kullanıcı Tesisi")
    invitation = create_invite(
        client,
        admin,
        "new-invited-user@example.com",
        role="technician",
        notify=False,
    )
    token = invitation["test_token"]

    preview = client.get(f"/api/v1/invitations/{token}")
    assert preview.status_code == 200, preview.text
    assert preview.json()["organization_name"] == "Davet Yeni Kullanıcı Tesisi"
    assert preview.json()["email"] == "new-invited-user@example.com"
    assert preview.json()["role"] == "technician"
    assert preview.json()["existing_user"] is False

    missing_password = client.post(
        "/api/v1/invitations/accept",
        json={"token": token},
    )
    assert missing_password.status_code == 422
    assert missing_password.json()["detail"]["code"] == "PASSWORD_REQUIRED"

    accepted = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": PASSWORD},
    )
    assert accepted.status_code == 201, accepted.text
    payload = accepted.json()
    assert payload["created_user"] is True
    assert payload["organization"]["id"] == admin["organization"]["id"]
    assert payload["user"]["email"] == "new-invited-user@example.com"
    assert payload["user"]["is_email_verified"] is True

    invited_headers = headers(payload, admin["organization"]["id"])
    assert client.get("/api/v1/locations", headers=invited_headers).status_code == 200
    assert client.post(
        "/api/v1/locations",
        headers=invited_headers,
        json={"name": "Teknisyen Lokasyonu", "facility_type": "hotel"},
    ).status_code == 201
    assert client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=invited_headers,
        json={"email": "yetkisiz@example.com", "role": "viewer"},
    ).status_code == 403

    repeated = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": PASSWORD},
    )
    assert repeated.status_code == 400

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == "new-invited-user@example.com"))
        membership = db.scalar(
            select(Membership).where(
                Membership.user_id == user.id,
                Membership.organization_id == admin["organization"]["id"],
            )
        )
        assert membership and membership.role == Role.technician
        assert membership.notify_incidents is False
        message = db.scalar(
            select(EmailOutbox)
            .where(
                EmailOutbox.organization_id == admin["organization"]["id"],
                EmailOutbox.template == "organization_invitation",
            )
            .order_by(EmailOutbox.created_at.desc())
        )
        assert message is not None
        assert token not in message.payload_json
        decrypted = read_payload(message)
        assert decrypted["token"] == token
        assert decrypted["role"] == "technician"


def test_existing_user_requires_password_and_can_accept(client):
    admin = register(client, "invite-admin-existing@example.com", "Davet Mevcut Kullanıcı Tesisi")
    existing = register(client, "existing-invited-user@example.com", "Mevcut Kullanıcının Kuruluşu")
    invitation = create_invite(client, admin, "existing-invited-user@example.com", role="viewer")
    token = invitation["test_token"]

    preview = client.get(f"/api/v1/invitations/{token}")
    assert preview.status_code == 200
    assert preview.json()["existing_user"] is True

    no_password = client.post("/api/v1/invitations/accept", json={"token": token})
    assert no_password.status_code == 401
    assert no_password.json()["detail"]["code"] == "EXISTING_ACCOUNT_AUTH_REQUIRED"

    wrong_password = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": "Yanlis-Parola-2026"},
    )
    assert wrong_password.status_code == 401

    accepted = client.post(
        "/api/v1/invitations/accept",
        json={"token": token, "password": PASSWORD},
    )
    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["created_user"] is False
    assert accepted.json()["user"]["id"] == existing["user"]["id"]


def test_invitation_refresh_revocation_expiry_and_plan_capacity(client):
    admin = register(client, "invite-admin-rules@example.com", "Davet Kural Tesisi")
    first = create_invite(client, admin, "refresh@example.com")
    refreshed = create_invite(client, admin, "refresh@example.com", role="technician")
    assert refreshed["id"] == first["id"]
    assert refreshed["test_token"] != first["test_token"]
    assert client.get(f"/api/v1/invitations/{first['test_token']}").status_code == 400
    assert client.get(f"/api/v1/invitations/{refreshed['test_token']}").status_code == 200

    revoked = client.delete(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations/{refreshed['id']}",
        headers=headers(admin),
    )
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["status"] == "revoked"
    assert client.post(
        "/api/v1/invitations/accept",
        json={"token": refreshed["test_token"], "password": PASSWORD},
    ).status_code == 400

    expired = create_invite(client, admin, "expired@example.com")
    with SessionLocal() as db:
        row = db.get(OrganizationInvitation, expired["id"])
        row.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert client.get(f"/api/v1/invitations/{expired['test_token']}").status_code == 400

    # Revoked/expired invitations kapasiteyi tüketmez. İki aktif pending davet,
    # mevcut admin ile pilot planın üç üyelik kapasitesini tamamen rezerve eder.
    create_invite(client, admin, "pending-one@example.com")
    create_invite(client, admin, "pending-two@example.com")
    over = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=headers(admin),
        json={"email": "pending-three@example.com", "role": "viewer"},
    )
    assert over.status_code == 409
    assert over.json()["detail"]["code"] == "PLAN_LIMIT_REACHED"
    assert over.json()["detail"]["pending_invitations"] == 2


def test_existing_member_cannot_be_invited(client):
    admin = register(client, "invite-admin-member@example.com", "Davet Üye Tesisi")
    second = register(client, "already-member@example.com", "İkinci Üye Kuruluşu")
    add_member = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/members",
        headers=headers(admin),
        json={"email": "already-member@example.com", "role": "viewer", "notify_incidents": True},
    )
    assert add_member.status_code == 200, add_member.text
    invitation = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=headers(admin),
        json={"email": "already-member@example.com", "role": "viewer"},
    )
    assert invitation.status_code == 409
    assert "zaten kuruluş üyesi" in invitation.json()["detail"]
    assert second
