from __future__ import annotations

from datetime import timedelta

import pytest
from sqlalchemy import select

from app.db import SessionLocal
from app.kg_models import KnowledgeAssertion, KnowledgeEntity, KnowledgeSource
from app.kg_service import GLOBAL_SCOPE, upsert_assertion, upsert_entity, upsert_source
from app.models import Membership, Role, utcnow

PASSWORD = "Guvenli-Knowledge-Graph-2026"


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


def create_entity(client, auth: dict, key: str, *, kind: str = "Asset", name: str | None = None):
    return client.post(
        "/api/v1/kg/entities",
        headers=headers(auth),
        json={
            "canonical_key": key,
            "kind": kind,
            "name": name or key,
            "description": f"{key} test varlığı",
            "properties": {"test": True},
        },
    )


def create_source(client, auth: dict, key: str):
    return client.post(
        "/api/v1/kg/sources",
        headers=headers(auth),
        json={
            "canonical_key": key,
            "name": f"{key} kaynağı",
            "source_type": "inspection",
            "authority_score": 0.9,
            "last_checked_at": utcnow().isoformat(),
        },
    )


def create_assertion(
    client,
    auth: dict,
    *,
    subject_id: str,
    source_id: str,
    predicate: str = "locatedAt",
    object_id: str | None = None,
    literal_value=None,
    verified_at=None,
):
    payload = {
        "subject_entity_id": subject_id,
        "predicate": predicate,
        "source_id": source_id,
        "confidence": 0.92,
        "properties": {"method": "test"},
    }
    if object_id:
        payload["object_entity_id"] = object_id
    else:
        payload["literal_value"] = literal_value
    if verified_at:
        payload["verified_at"] = verified_at.isoformat()
    return client.post("/api/v1/kg/assertions", headers=headers(auth), json=payload)


def seed_public_fixture(canonical_suffix: str = "main") -> dict[str, str]:
    with SessionLocal() as db:
        source, _ = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"source:test:{canonical_suffix}",
            name=f"Public test source {canonical_suffix}",
            source_type="official",
            url=f"https://example.com/{canonical_suffix}",
            authority_score=1.0,
            status="active",
            last_checked_at=utcnow(),
        )
        company, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"distribution-company:test-{canonical_suffix}",
            kind="DistributionCompany",
            name=f"Test EDAŞ {canonical_suffix}",
            description="Public dağıtım şirketi test varlığı",
            properties={"url": "https://www.alo186.com/dagitim-sirketleri/test"},
            is_public=True,
        )
        province, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"province:test-{canonical_suffix}",
            kind="Province",
            name=f"Test İl {canonical_suffix}",
            is_public=True,
        )
        hidden, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"hidden:test-{canonical_suffix}",
            kind="InternalEntity",
            name=f"Hidden {canonical_suffix}",
            is_public=False,
        )
        assertion, _ = upsert_assertion(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            subject_entity_id=province.id,
            predicate="servedBy",
            object_entity_id=company.id,
            source_id=source.id,
            confidence=1.0,
            is_public=True,
            verified_at=utcnow(),
            evidence={"fixture": canonical_suffix},
        )
        db.commit()
        return {
            "source_id": source.id,
            "company_id": company.id,
            "province_id": province.id,
            "hidden_id": hidden.id,
            "assertion_id": assertion.id,
            "company_key": company.canonical_key,
            "province_key": province.canonical_key,
            "hidden_key": hidden.canonical_key,
        }


def test_public_search_and_entity_bundle_hide_private_global_entities(client):
    fixture = seed_public_fixture("search")

    search = client.get("/api/v1/kg/public/search", params={"q": "Test"})
    assert search.status_code == 200, search.text
    keys = {item["canonical_key"] for item in search.json()["items"]}
    assert fixture["company_key"] in keys
    assert fixture["province_key"] in keys
    assert fixture["hidden_key"] not in keys

    bundle = client.get(f"/api/v1/kg/public/entities/{fixture['province_key']}")
    assert bundle.status_code == 200, bundle.text
    assert bundle.json()["entity"]["canonical_key"] == fixture["province_key"]
    assert bundle.json()["assertions"][0]["predicate"] == "servedBy"
    assert bundle.json()["sources"][0]["url"].startswith("https://example.com/")


def test_public_jsonld_contains_relation_source_and_confidence(client):
    fixture = seed_public_fixture("jsonld")
    response = client.get(f"/api/v1/kg/public/entities/{fixture['province_key']}/jsonld")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["@type"] == "Province"
    assert payload["servedBy"]["@type"] == "DistributionCompany"
    assert payload["servedBy"]["confidence"] == 1.0
    assert payload["servedBy"]["source"].startswith("https://example.com/")


def test_public_entity_404_for_private_or_unknown_key(client):
    fixture = seed_public_fixture("private")
    hidden = client.get(f"/api/v1/kg/public/entities/{fixture['hidden_key']}")
    assert hidden.status_code == 404
    missing = client.get("/api/v1/kg/public/entities/not:found")
    assert missing.status_code == 404


def test_tenant_entity_source_and_literal_assertion_crud(client):
    auth = register(client, "kg-admin-1@example.com", "KG Kuruluş 1")
    entity_response = create_entity(client, auth, "asset:kg-admin-1", name="Ana Jeneratör")
    assert entity_response.status_code == 201, entity_response.text
    entity = entity_response.json()
    source_response = create_source(client, auth, "source:inspection:kg-admin-1")
    assert source_response.status_code == 201, source_response.text
    source = source_response.json()

    assertion_response = create_assertion(
        client,
        auth,
        subject_id=entity["id"],
        source_id=source["id"],
        predicate="ratedPowerKva",
        literal_value={"value": 630, "unit": "kVA"},
        verified_at=utcnow(),
    )
    assert assertion_response.status_code == 201, assertion_response.text
    assertion = assertion_response.json()
    assert assertion["literal_value"]["value"] == 630
    assert assertion["evidence_hash"] is None

    bundle = client.get(f"/api/v1/kg/entities/{entity['id']}", headers=headers(auth))
    assert bundle.status_code == 200, bundle.text
    assert bundle.json()["entity"]["scope_key"].startswith("org:")
    assert bundle.json()["assertions"][0]["predicate"] == "ratedPowerKva"

    patched = client.patch(
        f"/api/v1/kg/entities/{entity['id']}",
        headers=headers(auth),
        json={"name": "Ana Jeneratör Revize", "properties": {"serial": "GEN-001"}},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "Ana Jeneratör Revize"
    assert patched.json()["properties"]["serial"] == "GEN-001"

    assertion_patch = client.patch(
        f"/api/v1/kg/assertions/{assertion['id']}",
        headers=headers(auth),
        json={"confidence": 0.75, "status": "disputed"},
    )
    assert assertion_patch.status_code == 200, assertion_patch.text
    assert assertion_patch.json()["confidence"] == 0.75
    assert assertion_patch.json()["status"] == "disputed"


def test_assertion_requires_exactly_one_object_or_literal(client):
    auth = register(client, "kg-admin-2@example.com", "KG Kuruluş 2")
    subject = create_entity(client, auth, "asset:kg-admin-2").json()
    target = create_entity(client, auth, "location:kg-admin-2", kind="Location").json()
    source = create_source(client, auth, "source:inspection:kg-admin-2").json()

    neither = client.post(
        "/api/v1/kg/assertions",
        headers=headers(auth),
        json={"subject_entity_id": subject["id"], "predicate": "locatedAt", "source_id": source["id"]},
    )
    assert neither.status_code == 422

    both = client.post(
        "/api/v1/kg/assertions",
        headers=headers(auth),
        json={
            "subject_entity_id": subject["id"],
            "predicate": "locatedAt",
            "source_id": source["id"],
            "object_entity_id": target["id"],
            "literal_value": "hatalı",
        },
    )
    assert both.status_code == 422


def test_assertion_rejects_missing_or_foreign_source(client):
    first = register(client, "kg-admin-3a@example.com", "KG Kuruluş 3A")
    second = register(client, "kg-admin-3b@example.com", "KG Kuruluş 3B")
    entity = create_entity(client, first, "asset:kg-admin-3a").json()
    foreign_source = create_source(client, second, "source:foreign:kg-admin-3b").json()

    missing = create_assertion(
        client,
        first,
        subject_id=entity["id"],
        source_id="00000000-0000-0000-0000-000000000000",
        predicate="status",
        literal_value="active",
    )
    assert missing.status_code == 404

    foreign = create_assertion(
        client,
        first,
        subject_id=entity["id"],
        source_id=foreign_source["id"],
        predicate="status",
        literal_value="active",
    )
    assert foreign.status_code == 404


def test_tenant_isolation_hides_private_entities_and_assertions(client):
    first = register(client, "kg-isolation-a@example.com", "KG Isolation A")
    second = register(client, "kg-isolation-b@example.com", "KG Isolation B")
    entity = create_entity(client, first, "asset:isolation-a").json()
    source = create_source(client, first, "source:isolation-a").json()
    create_assertion(
        client,
        first,
        subject_id=entity["id"],
        source_id=source["id"],
        predicate="status",
        literal_value="private",
    )

    direct = client.get(f"/api/v1/kg/entities/{entity['id']}", headers=headers(second))
    assert direct.status_code == 404
    listing = client.get("/api/v1/kg/entities", headers=headers(second), params={"q": "isolation-a"})
    assert listing.status_code == 200
    assert listing.json()["count"] == 0


def test_tenant_can_read_but_not_mutate_global_public_entity(client):
    fixture = seed_public_fixture("tenant-global")
    auth = register(client, "kg-global-reader@example.com", "KG Global Reader")

    bundle = client.get(f"/api/v1/kg/entities/{fixture['company_id']}", headers=headers(auth))
    assert bundle.status_code == 200, bundle.text
    assert bundle.json()["entity"]["scope_key"] == "global"

    patch = client.patch(
        f"/api/v1/kg/entities/{fixture['company_id']}",
        headers=headers(auth),
        json={"name": "Değiştirilemez"},
    )
    assert patch.status_code == 403
    delete = client.delete(f"/api/v1/kg/entities/{fixture['company_id']}", headers=headers(auth))
    assert delete.status_code == 403


def test_viewer_can_read_but_cannot_write_knowledge_graph(client):
    admin = register(client, "kg-viewer-admin@example.com", "KG Viewer Org")
    viewer = register(client, "kg-viewer-user@example.com", "KG Viewer Own Org")
    entity = create_entity(client, admin, "asset:viewer-test").json()

    with SessionLocal() as db:
        db.add(
            Membership(
                user_id=viewer["user"]["id"],
                organization_id=admin["organization"]["id"],
                role=Role.viewer,
            )
        )
        db.commit()

    viewer_headers = headers(viewer, admin["organization"]["id"])
    read = client.get(f"/api/v1/kg/entities/{entity['id']}", headers=viewer_headers)
    assert read.status_code == 200
    write = client.post(
        "/api/v1/kg/entities",
        headers=viewer_headers,
        json={"canonical_key": "asset:viewer-forbidden", "kind": "Asset", "name": "Yasak"},
    )
    assert write.status_code == 403


def test_entity_and_assertion_upserts_are_idempotent(client):
    auth = register(client, "kg-idempotent@example.com", "KG Idempotent")
    first_entity = create_entity(client, auth, "asset:idempotent", name="İlk Ad").json()
    second_entity = create_entity(client, auth, "asset:idempotent", name="İkinci Ad").json()
    assert first_entity["id"] == second_entity["id"]
    assert second_entity["name"] == "İkinci Ad"

    source = create_source(client, auth, "source:idempotent").json()
    first_assertion = create_assertion(
        client,
        auth,
        subject_id=first_entity["id"],
        source_id=source["id"],
        predicate="status",
        literal_value="active",
    ).json()
    second_assertion = create_assertion(
        client,
        auth,
        subject_id=first_entity["id"],
        source_id=source["id"],
        predicate="status",
        literal_value="active",
    ).json()
    assert first_assertion["id"] == second_assertion["id"]
    assert first_assertion["fingerprint"] == second_assertion["fingerprint"]


def test_bounded_graph_path_finds_two_hop_route(client):
    auth = register(client, "kg-path@example.com", "KG Path Org")
    source = create_source(client, auth, "source:path").json()
    first = create_entity(client, auth, "asset:path-a").json()
    middle = create_entity(client, auth, "location:path-b", kind="Location").json()
    last = create_entity(client, auth, "incident:path-c", kind="Incident").json()
    assert create_assertion(client, auth, subject_id=first["id"], source_id=source["id"], object_id=middle["id"]).status_code == 201
    assert create_assertion(client, auth, subject_id=middle["id"], source_id=source["id"], predicate="affectedBy", object_id=last["id"]).status_code == 201

    path = client.get(
        "/api/v1/kg/path",
        headers=headers(auth),
        params={"from_id": first["id"], "to_id": last["id"], "max_depth": 3},
    )
    assert path.status_code == 200, path.text
    assert path.json()["depth"] == 2
    assert len(path.json()["path"]) == 2

    too_shallow = client.get(
        "/api/v1/kg/path",
        headers=headers(auth),
        params={"from_id": first["id"], "to_id": last["id"], "max_depth": 1},
    )
    assert too_shallow.status_code == 404


def test_public_path_uses_only_public_global_edges(client):
    first = seed_public_fixture("path-public")
    hidden = seed_public_fixture("path-hidden")
    with SessionLocal() as db:
        source = db.get(KnowledgeSource, first["source_id"])
        private_edge, _ = upsert_assertion(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            subject_entity_id=first["company_id"],
            predicate="derivedFrom",
            object_entity_id=hidden["hidden_id"],
            source_id=source.id,
            confidence=1.0,
            is_public=False,
            verified_at=utcnow(),
        )
        db.commit()
        assert private_edge.is_public is False

    visible = client.get(
        "/api/v1/kg/public/path",
        params={"from_key": first["province_key"], "to_key": first["company_key"], "max_depth": 2},
    )
    assert visible.status_code == 200
    private = client.get(
        "/api/v1/kg/public/path",
        params={"from_key": first["company_key"], "to_key": hidden["hidden_key"], "max_depth": 2},
    )
    assert private.status_code == 404


def test_graph_health_detects_stale_orphan_low_confidence_expired_and_conflicts(client):
    auth = register(client, "kg-health@example.com", "KG Health Org")
    source_one = create_source(client, auth, "source:health-1").json()
    source_two = create_source(client, auth, "source:health-2").json()
    subject = create_entity(client, auth, "asset:health-subject").json()
    create_entity(client, auth, "asset:health-orphan")

    stale = create_assertion(
        client,
        auth,
        subject_id=subject["id"],
        source_id=source_one["id"],
        predicate="temperatureStatus",
        literal_value="hot",
        verified_at=utcnow() - timedelta(days=90),
    )
    assert stale.status_code == 201
    low = create_assertion(
        client,
        auth,
        subject_id=subject["id"],
        source_id=source_one["id"],
        predicate="confidenceTest",
        literal_value="uncertain",
    )
    assert low.status_code == 201
    client.patch(
        f"/api/v1/kg/assertions/{low.json()['id']}",
        headers=headers(auth),
        json={"confidence": 0.2, "valid_to": (utcnow() - timedelta(days=1)).isoformat()},
    )
    create_assertion(
        client,
        auth,
        subject_id=subject["id"],
        source_id=source_one["id"],
        predicate="operatingState",
        literal_value="normal",
    )
    create_assertion(
        client,
        auth,
        subject_id=subject["id"],
        source_id=source_two["id"],
        predicate="operatingState",
        literal_value="fault",
    )

    health = client.get("/api/v1/kg/health", headers=headers(auth), params={"stale_days": 30})
    assert health.status_code == 200, health.text
    payload = health.json()
    assert payload["orphan_entities"] >= 1
    assert payload["stale_assertions"] >= 1
    assert payload["low_confidence_assertions"] >= 1
    assert payload["expired_assertions"] >= 1
    assert payload["conflicting_literal_claims"] >= 1
    assert payload["score"] < 100


def test_verification_updates_source_and_disputes_changed_assertion(client):
    auth = register(client, "kg-verify@example.com", "KG Verify Org")
    source = create_source(client, auth, "source:verify").json()
    entity = create_entity(client, auth, "asset:verify").json()
    assertion = create_assertion(
        client,
        auth,
        subject_id=entity["id"],
        source_id=source["id"],
        predicate="status",
        literal_value="active",
    ).json()
    verification = client.post(
        "/api/v1/kg/verifications",
        headers=headers(auth),
        json={
            "source_id": source["id"],
            "target_assertion_id": assertion["id"],
            "status": "changed",
            "duration_ms": 125,
            "content_hash": "a" * 64,
            "details": {"reason": "source changed"},
        },
    )
    assert verification.status_code == 201, verification.text
    with SessionLocal() as db:
        source_row = db.get(KnowledgeSource, source["id"])
        assertion_row = db.get(KnowledgeAssertion, assertion["id"])
        assert source_row.status == "changed"
        assert source_row.content_hash == "a" * 64
        assert assertion_row.status == "disputed"
        assert assertion_row.verified_at is not None


def test_retire_assertion_and_entity_are_soft_deletes(client):
    auth = register(client, "kg-retire@example.com", "KG Retire Org")
    source = create_source(client, auth, "source:retire").json()
    entity = create_entity(client, auth, "asset:retire").json()
    assertion = create_assertion(
        client,
        auth,
        subject_id=entity["id"],
        source_id=source["id"],
        predicate="status",
        literal_value="active",
    ).json()

    assert client.delete(f"/api/v1/kg/assertions/{assertion['id']}", headers=headers(auth)).status_code == 204
    bundle = client.get(f"/api/v1/kg/entities/{entity['id']}", headers=headers(auth)).json()
    assert not bundle["assertions"]

    assert client.delete(f"/api/v1/kg/entities/{entity['id']}", headers=headers(auth)).status_code == 204
    retired = client.get(f"/api/v1/kg/entities/{entity['id']}", headers=headers(auth))
    assert retired.status_code == 200
    assert retired.json()["entity"]["status"] == "retired"


def test_public_health_exports_prometheus_gauges(client):
    seed_public_fixture("metrics")
    health = client.get("/api/v1/kg/public/health")
    assert health.status_code == 200, health.text
    metrics_response = client.get("/metrics", headers={"X-Metrics-Token": "test-metrics-token"})
    assert metrics_response.status_code == 200
    text = metrics_response.text
    assert 'alo186_kg_health_score{scope="public"}' in text
    assert 'alo186_kg_entities{scope="public"}' in text
    assert 'alo186_kg_assertions{scope="public"}' in text


@pytest.mark.parametrize("kind", ["Asset", "CriticalLoad", "Incident", "IncidentTask", "Location", "Standard", "Regulation"])
def test_supported_tenant_entity_kinds_are_searchable(client, kind):
    auth = register(client, f"kg-kind-{kind.lower()}@example.com", f"KG Kind {kind}")
    response = create_entity(client, auth, f"entity:{kind.lower()}", kind=kind, name=f"{kind} Aranabilir")
    assert response.status_code == 201, response.text
    listing = client.get(
        "/api/v1/kg/entities",
        headers=headers(auth),
        params={"q": "Aranabilir", "kind": kind},
    )
    assert listing.status_code == 200
    assert listing.json()["count"] == 1
    assert listing.json()["items"][0]["kind"] == kind
