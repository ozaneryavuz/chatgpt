from __future__ import annotations

from datetime import timedelta

from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import AuditLog, EmailOutbox, OrganizationInvitation, User, utcnow
from app.notifications import read_payload

PASSWORD = "Guvenli-Davet-Parolasi-2026"


def register(client, email: str, organization_name: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "organization_name": organization_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict, organization_id: str | None = None) -> dict[str, str]:
    result = {"Authorization": f"Bearer {auth['access_token']}"}
    if organization_id or auth.get("organization"):
        result["X-Organization-ID"] = organization_id or auth["organization"]["id"]
    return result


def create_invitation(client, auth: dict, email: str, role: str = "viewer", notify: bool = True):
    organization_id = auth["organization"]["id"]
    return client.post(
        f"/api/v1/organizations/{organization_id}/invitations",
        headers=headers(auth),
        json={"email": email, "role": role, "notify_incidents": notify},
    )


def test_admin_invites_new_user_and_token_is_single_use(client):
    admin = register(client, "invite-admin-1@example.com", "Davet Test Kuruluşu 1")
    invited_email = "invite-new-user-1@example.com"

    invitation_response = create_invitation(client, admin, invited_email, role="technician", notify=False)
    assert invitation_response.status_code == 201, invitation_response.text
    invitation = invitation_response.json()
    token = invitation["test_token"]
    assert token
    assert invitation["role"] == "technician"
    assert invitation["notify_incidents"] is False
    assert invitation["status"] == "pending"

    preview = client.post("/api/v1/invitations/preview", json={"token": token})
    assert preview.status_code == 200, preview.text
    assert preview.json()["organization_name"] == "Davet Test Kuruluşu 1"
    assert preview.json()["role"] == "technician"
    assert preview.json()["existing_account"] is False
    assert preview.json()["email_masked"] != invited_email

    with SessionLocal() as db:
        row = db.scalar(
            select(OrganizationInvitation).where(OrganizationInvitation.id == invitation["id"])
        )
        assert row is not None
        assert token not in row.token_hash
        outbox = db.scalar(
            select(EmailOutbox)
            .where(
                EmailOutbox.organization_id == admin["organization"]["id"],
                EmailOutbox.to_email == invited_email,
                EmailOutbox.template == "organization_invitation",
            )
            .order_by(EmailOutbox.created_at.desc())
        )
        assert outbox is not None
        assert token not in outbox.payload_json
        payload = read_payload(outbox)
        assert payload["token"] == token
        assert payload["role"] == "technician"

    accepted = client.post(
        "/api/v1/invitations/accept-new",
        json={"token": token, "password": PASSWORD},
    )
    assert accepted.status_code == 201, accepted.text
    accepted_auth = accepted.json()
    assert accepted_auth["user"]["email"] == invited_email
    assert accepted_auth["user"]["is_email_verified"] is True
    assert accepted_auth["organization"]["id"] == admin["organization"]["id"]

    memberships = client.get(
        "/api/v1/auth/memberships",
        headers={"Authorization": f"Bearer {accepted_auth['access_token']}"},
    )
    assert memberships.status_code == 200, memberships.text
    assert memberships.json()[0]["role"] == "technician"
    assert memberships.json()[0]["notify_incidents"] is False

    repeated = client.post(
        "/api/v1/invitations/accept-new",
        json={"token": token, "password": PASSWORD},
    )
    assert repeated.status_code == 400


def test_non_admin_cannot_invite_and_existing_account_can_accept(client):
    admin = register(client, "invite-admin-2@example.com", "Davet Test Kuruluşu 2")
    technician_email = "invite-technician-2@example.com"
    technician_invite = create_invitation(client, admin, technician_email, role="technician")
    technician_token = technician_invite.json()["test_token"]
    technician_auth_response = client.post(
        "/api/v1/invitations/accept-new",
        json={"token": technician_token, "password": PASSWORD},
    )
    assert technician_auth_response.status_code == 201, technician_auth_response.text
    technician_auth = technician_auth_response.json()

    forbidden = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=headers(technician_auth, admin["organization"]["id"]),
        json={"email": "should-not-invite@example.com", "role": "viewer"},
    )
    assert forbidden.status_code == 403

    existing = register(client, "existing-invitee-2@example.com", "Kendi Kuruluşu 2")
    invite_existing = create_invitation(
        client,
        admin,
        "existing-invitee-2@example.com",
        role="viewer",
        notify=False,
    )
    assert invite_existing.status_code == 201, invite_existing.text
    token = invite_existing.json()["test_token"]

    preview = client.post("/api/v1/invitations/preview", json={"token": token})
    assert preview.status_code == 200
    assert preview.json()["existing_account"] is True

    accepted = client.post(
        "/api/v1/invitations/accept-existing",
        headers={"Authorization": f"Bearer {existing['access_token']}"},
        json={"token": token},
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["role"] == "viewer"
    assert accepted.json()["notify_incidents"] is False

    memberships = client.get(
        "/api/v1/auth/memberships",
        headers={"Authorization": f"Bearer {existing['access_token']}"},
    )
    assert memberships.status_code == 200
    organization_ids = {item["organization"]["id"] for item in memberships.json()}
    assert existing["organization"]["id"] in organization_ids
    assert admin["organization"]["id"] in organization_ids


def test_duplicate_active_invitation_rotates_token_and_resend_revoke_work(client):
    admin = register(client, "invite-admin-3@example.com", "Davet Test Kuruluşu 3")
    email = "duplicate-invite-3@example.com"

    first = create_invitation(client, admin, email, role="viewer")
    assert first.status_code == 201, first.text
    first_data = first.json()
    first_token = first_data["test_token"]

    second = create_invitation(client, admin, email, role="technician", notify=False)
    assert second.status_code == 201, second.text
    second_data = second.json()
    second_token = second_data["test_token"]
    assert second_data["id"] == first_data["id"]
    assert second_data["role"] == "technician"
    assert second_data["resend_count"] == 1
    assert second_token != first_token
    assert client.post("/api/v1/invitations/preview", json={"token": first_token}).status_code == 400
    assert client.post("/api/v1/invitations/preview", json={"token": second_token}).status_code == 200

    with SessionLocal() as db:
        count = int(
            db.scalar(
                select(func.count(OrganizationInvitation.id)).where(
                    OrganizationInvitation.organization_id == admin["organization"]["id"],
                    OrganizationInvitation.email == email,
                    OrganizationInvitation.accepted_at.is_(None),
                    OrganizationInvitation.revoked_at.is_(None),
                )
            )
            or 0
        )
        assert count == 1

    resent = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations/{second_data['id']}/resend",
        headers=headers(admin),
    )
    assert resent.status_code == 200, resent.text
    resent_data = resent.json()
    resent_token = resent_data["test_token"]
    assert resent_data["resend_count"] == 2
    assert resent_token != second_token
    assert client.post("/api/v1/invitations/preview", json={"token": second_token}).status_code == 400

    revoked = client.delete(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations/{second_data['id']}",
        headers=headers(admin),
    )
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["status"] == "revoked"
    assert client.post("/api/v1/invitations/preview", json={"token": resent_token}).status_code == 400


def test_expired_invitation_and_email_mismatch_are_rejected(client):
    admin = register(client, "invite-admin-4@example.com", "Davet Test Kuruluşu 4")
    invite = create_invitation(client, admin, "expired-invite-4@example.com")
    token = invite.json()["test_token"]

    with SessionLocal() as db:
        row = db.scalar(select(OrganizationInvitation).where(OrganizationInvitation.id == invite.json()["id"]))
        row.expires_at = utcnow() - timedelta(seconds=1)
        db.commit()

    assert client.post("/api/v1/invitations/preview", json={"token": token}).status_code == 400

    mismatch_invite = create_invitation(client, admin, "target-mismatch-4@example.com")
    mismatch_token = mismatch_invite.json()["test_token"]
    other = register(client, "other-mismatch-4@example.com", "Başka Kuruluş 4")
    mismatch = client.post(
        "/api/v1/invitations/accept-existing",
        headers={"Authorization": f"Bearer {other['access_token']}"},
        json={"token": mismatch_token},
    )
    assert mismatch.status_code == 403


def test_pilot_member_limit_counts_pending_invitations(client):
    admin = register(client, "invite-admin-5@example.com", "Davet Test Kuruluşu 5")
    first = create_invitation(client, admin, "pending-one-5@example.com")
    second = create_invitation(client, admin, "pending-two-5@example.com")
    assert first.status_code == 201
    assert second.status_code == 201

    blocked = create_invitation(client, admin, "pending-three-5@example.com")
    assert blocked.status_code == 409, blocked.text
    detail = blocked.json()["detail"]
    assert detail["code"] == "PLAN_LIMIT_REACHED"
    assert detail["current_members"] == 1
    assert detail["pending_invitations"] == 2
    assert detail["limit"] == 3


def test_invitation_list_and_audit_records(client):
    admin = register(client, "invite-admin-6@example.com", "Davet Test Kuruluşu 6")
    created = create_invitation(client, admin, "list-invite-6@example.com", role="admin")
    assert created.status_code == 201

    listed = client.get(
        f"/api/v1/organizations/{admin['organization']['id']}/invitations",
        headers=headers(admin),
    )
    assert listed.status_code == 200, listed.text
    assert len(listed.json()) == 1
    assert listed.json()[0]["test_token"] is None
    assert listed.json()[0]["role"] == "admin"

    with SessionLocal() as db:
        audit_actions = set(
            db.scalars(
                select(AuditLog.action).where(
                    AuditLog.organization_id == admin["organization"]["id"]
                )
            ).all()
        )
        assert "invitation.created" in audit_actions
        user = db.scalar(select(User).where(User.email == "list-invite-6@example.com"))
        assert user is None
