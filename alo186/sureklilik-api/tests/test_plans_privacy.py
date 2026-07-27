from __future__ import annotations


def register(client, email: str, organization_name: str, password: str = "Guvenli-Parola-2026"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "organization_name": organization_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict, organization_id: str | None = None) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Organization-ID": organization_id or auth["organization"]["id"],
    }


def test_pilot_plan_limits_and_usage_endpoint(client):
    admin = register(client, "plan-admin@example.com", "Plan Limit Tesisi")
    admin_headers = headers(admin)

    usage = client.get("/api/v1/billing/usage", headers=admin_headers)
    assert usage.status_code == 200, usage.text
    payload = usage.json()
    assert payload["plan"] == "pilot"
    assert payload["usage"]["members"] == 1
    assert payload["limits"]["locations"] == 3
    assert payload["remaining"]["members"] == 2

    for index in range(3):
        response = client.post(
            "/api/v1/locations",
            headers=admin_headers,
            json={"name": f"Lokasyon {index + 1}", "facility_type": "hotel"},
        )
        assert response.status_code == 201, response.text
    exceeded = client.post(
        "/api/v1/locations",
        headers=admin_headers,
        json={"name": "Dördüncü Lokasyon", "facility_type": "hotel"},
    )
    assert exceeded.status_code == 409
    assert exceeded.json()["detail"]["code"] == "PLAN_LIMIT_REACHED"
    assert exceeded.json()["detail"]["resource"] == "locations"

    second = register(client, "plan-member-2@example.com", "İkinci Kuruluş")
    third = register(client, "plan-member-3@example.com", "Üçüncü Kuruluş")
    fourth = register(client, "plan-member-4@example.com", "Dördüncü Kuruluş")
    for email in ("plan-member-2@example.com", "plan-member-3@example.com"):
        response = client.post(
            f"/api/v1/organizations/{admin['organization']['id']}/members",
            headers=admin_headers,
            json={"email": email, "role": "viewer", "notify_incidents": True},
        )
        assert response.status_code == 200, response.text
    over_member = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/members",
        headers=admin_headers,
        json={"email": "plan-member-4@example.com", "role": "viewer", "notify_incidents": True},
    )
    assert over_member.status_code == 409
    assert over_member.json()["detail"]["resource"] == "members"
    assert second and third and fourth


def test_privacy_export_sole_admin_guard_and_deletion_requests(client):
    first = register(client, "privacy-owner@example.com", "KVKK Pilot Oteli")
    first_headers = headers(first)

    exported = client.get("/api/v1/privacy/me/export", headers=first_headers)
    assert exported.status_code == 200, exported.text
    data = exported.json()["data"]
    assert data["user"]["email"] == "privacy-owner@example.com"
    serialized = str(data).lower()
    assert "password_hash" not in serialized
    assert "mfa_secret" not in serialized

    sole_admin = client.post(
        "/api/v1/privacy/me/delete-request",
        headers=first_headers,
        json={"password": "Guvenli-Parola-2026", "confirmation": "HESABIMI SIL"},
    )
    assert sole_admin.status_code == 409
    assert sole_admin.json()["detail"]["code"] == "SOLE_ADMIN"

    second = register(client, "privacy-second-admin@example.com", "Yedek Yönetici Kuruluşu")
    second_membership = client.post(
        f"/api/v1/organizations/{first['organization']['id']}/members",
        headers=first_headers,
        json={"email": "privacy-second-admin@example.com", "role": "admin", "notify_incidents": True},
    )
    assert second_membership.status_code == 200, second_membership.text

    delete_user = client.post(
        "/api/v1/privacy/me/delete-request",
        headers=first_headers,
        json={"password": "Guvenli-Parola-2026", "confirmation": "HESABIMI SIL"},
    )
    assert delete_user.status_code == 200, delete_user.text
    assert client.get("/api/v1/auth/me", headers=first_headers).status_code == 401

    second_on_first = headers(second, first["organization"]["id"])
    org_export = client.get("/api/v1/privacy/organization/export", headers=second_on_first)
    assert org_export.status_code == 200, org_export.text
    org_data = org_export.json()["data"]
    assert org_data["organization"]["name"] == "KVKK Pilot Oteli"

    delete_org = client.post(
        "/api/v1/privacy/organization/delete-request",
        headers=second_on_first,
        json={"password": "Guvenli-Parola-2026", "organization_name": "KVKK Pilot Oteli"},
    )
    assert delete_org.status_code == 200, delete_org.text
    assert client.get("/api/v1/locations", headers=second_on_first).status_code == 403
