from __future__ import annotations

from test_api import headers, register

# PR #16 Codex bulgularının tekrar oluşmasını engelleyen veri bütünlüğü testleri.


def test_last_admin_cannot_demote_self(client):
    admin = register(client, "guard-admin@example.com", "Yönetici Guard Tesisi")
    response = client.post(
        f"/api/v1/organizations/{admin['organization']['id']}/members",
        headers=headers(admin),
        json={"email": "guard-admin@example.com", "role": "viewer"},
    )
    assert response.status_code == 409, response.text
    assert "son yöneticisinin" in response.json()["detail"]


def test_backfilled_asset_test_does_not_move_last_test_backwards(client):
    admin = register(client, "guard-asset@example.com", "Varlık Tarih Guard Tesisi")
    location = client.post(
        "/api/v1/locations",
        headers=headers(admin),
        json={"name": "Guard Teknik Bina", "facility_type": "business"},
    ).json()
    asset = client.post(
        "/api/v1/assets",
        headers=headers(admin),
        json={
            "location_id": location["id"],
            "kind": "generator",
            "name": "Guard Jeneratör",
            "rated_power_kva": 250,
            "test_interval_days": 7,
        },
    ).json()

    newer_at = "2026-07-27T12:00:00Z"
    older_at = "2026-07-20T12:00:00Z"
    first = client.post(
        f"/api/v1/assets/{asset['id']}/tests",
        headers=headers(admin),
        json={"result": "passed", "tested_at": newer_at},
    )
    assert first.status_code == 200, first.text
    backfill = client.post(
        f"/api/v1/assets/{asset['id']}/tests",
        headers=headers(admin),
        json={"result": "passed", "tested_at": older_at},
    )
    assert backfill.status_code == 200, backfill.text

    assets = client.get("/api/v1/assets", headers=headers(admin)).json()
    stored = next(item for item in assets if item["id"] == asset["id"])
    assert stored["last_test_at"].startswith("2026-07-27T12:00:00")


def test_repeated_incident_close_is_idempotent(client):
    admin = register(client, "guard-close@example.com", "Kapanış Guard Tesisi")
    location = client.post(
        "/api/v1/locations",
        headers=headers(admin),
        json={"name": "Guard Olay Lokasyonu", "facility_type": "business"},
    ).json()
    incident = client.post(
        "/api/v1/incidents",
        headers=headers(admin),
        json={
            "location_id": location["id"],
            "kind": "outage",
            "summary": "İdempotent kapanış testi",
        },
    ).json()

    for task in incident["tasks"]:
        if task["is_required"]:
            completed = client.post(
                f"/api/v1/incidents/{incident['id']}/tasks/{task['id']}/complete",
                headers=headers(admin),
            )
            assert completed.status_code == 200, completed.text

    first = client.post(
        f"/api/v1/incidents/{incident['id']}/close",
        headers=headers(admin),
        json={"closure_note": "İlk kapanış"},
    )
    assert first.status_code == 200, first.text
    first_payload = first.json()

    repeated = client.post(
        f"/api/v1/incidents/{incident['id']}/close",
        headers=headers(admin),
        json={"closure_note": "Tekrarlanan kapanış"},
    )
    assert repeated.status_code == 200, repeated.text
    repeated_payload = repeated.json()
    assert repeated_payload["ended_at"] == first_payload["ended_at"]
    assert repeated_payload["summary"] == first_payload["summary"]
    assert "Tekrarlanan kapanış" not in repeated_payload["summary"]

    audit = client.get("/api/v1/audit-logs", headers=headers(admin)).json()
    entries = [
        item
        for item in audit
        if item["action"] == "incident.closed" and item["entity_id"] == incident["id"]
    ]
    assert len(entries) == 1
