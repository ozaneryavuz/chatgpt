from __future__ import annotations


def register(client, email: str, organization_name: str):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "Guvenli-Parola-2026",
            "organization_name": organization_name,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Organization-ID": auth["organization"]["id"],
    }


def test_tenant_isolation_roles_and_incident_guard(client):
    admin = register(client, "admin@example.com", "Pilot Otel")

    location_response = client.post(
        "/api/v1/locations",
        headers=headers(admin),
        json={
            "name": "Ana Tesis",
            "city": "Muğla",
            "district": "Marmaris",
            "facility_type": "hotel",
        },
    )
    assert location_response.status_code == 201, location_response.text
    location = location_response.json()

    load_response = client.post(
        "/api/v1/critical-loads",
        headers=headers(admin),
        json={
            "location_id": location["id"],
            "name": "Yangın Algılama Sistemi",
            "priority": "P1",
            "power_kw": 0.5,
            "backup_source": "UPS",
            "autonomy_minutes": 120,
            "owner_name": "Teknik Müdür",
        },
    )
    assert load_response.status_code == 201, load_response.text

    incident_response = client.post(
        "/api/v1/incidents",
        headers=headers(admin),
        json={
            "location_id": location["id"],
            "kind": "outage",
            "summary": "Şebeke kesintisi tatbikatı",
        },
    )
    assert incident_response.status_code == 201, incident_response.text
    incident = incident_response.json()
    assert len(incident["tasks"]) >= 4
    assert any("Yangın Algılama" in task["title"] for task in incident["tasks"])

    close_response = client.post(
        f"/api/v1/incidents/{incident['id']}/close",
        headers=headers(admin),
        json={"closure_note": "Erken kapatma denemesi"},
    )
    assert close_response.status_code == 409
    assert "missing_tasks" in close_response.json()["detail"]

    for task in incident["tasks"]:
        if task["is_required"]:
            response = client.post(
                f"/api/v1/incidents/{incident['id']}/tasks/{task['id']}/complete",
                headers=headers(admin),
            )
            assert response.status_code == 200, response.text

    close_response = client.post(
        f"/api/v1/incidents/{incident['id']}/close",
        headers=headers(admin),
        json={"closure_note": "Tatbikat başarıyla tamamlandı"},
    )
    assert close_response.status_code == 200, close_response.text
    assert close_response.json()["status"] == "closed"

    second = register(client, "other@example.com", "Başka İşletme")
    forbidden_headers = {
        "Authorization": f"Bearer {second['access_token']}",
        "X-Organization-ID": admin["organization"]["id"],
    }
    assert client.get("/api/v1/locations", headers=forbidden_headers).status_code == 403

    add_member = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/members",
        headers=headers(admin),
        json={"email": "other@example.com", "role": "viewer"},
    )
    assert add_member.status_code == 200, add_member.text

    viewer_headers = {
        "Authorization": f"Bearer {second['access_token']}",
        "X-Organization-ID": admin["organization"]["id"],
    }
    assert client.get("/api/v1/locations", headers=viewer_headers).status_code == 200
    assert client.post(
        "/api/v1/locations",
        headers=viewer_headers,
        json={"name": "Yetkisiz Lokasyon", "facility_type": "hotel"},
    ).status_code == 403


def test_asset_test_and_audit(client):
    admin = register(client, "asset-admin@example.com", "Varlık Test Tesisi")
    loc = client.post(
        "/api/v1/locations",
        headers=headers(admin),
        json={"name": "Teknik Bina", "facility_type": "business"},
    ).json()

    asset_response = client.post(
        "/api/v1/assets",
        headers=headers(admin),
        json={
            "location_id": loc["id"],
            "kind": "generator",
            "name": "Jeneratör-1",
            "rated_power_kva": 630,
            "test_interval_days": 7,
        },
    )
    assert asset_response.status_code == 201, asset_response.text
    asset = asset_response.json()

    test_response = client.post(
        f"/api/v1/assets/{asset['id']}/tests",
        headers=headers(admin),
        json={"result": "passed", "notes": "Otomatik transfer başarılı."},
    )
    assert test_response.status_code == 200, test_response.text
    assert test_response.json()["result"] == "passed"

    audit_response = client.get("/api/v1/audit-logs", headers=headers(admin))
    assert audit_response.status_code == 200, audit_response.text
    actions = {item["action"] for item in audit_response.json()}
    assert "asset.created" in actions
    assert "asset_test.created" in actions
