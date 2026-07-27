from __future__ import annotations

from datetime import timedelta

from app.db import SessionLocal
from app.kg_models import KnowledgeAssertion, KnowledgeEntity, KnowledgeSource
from app.kg_service import GLOBAL_SCOPE, upsert_assertion, upsert_entity, upsert_source
from app.models import utcnow

PASSWORD = "Guvenli-KG-Review-2026"


def register(client, email: str, organization_name: str):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "organization_name": organization_name},
    )
    assert response.status_code == 201, response.text
    return response.json()


def headers(auth: dict) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Organization-ID": auth["organization"]["id"],
    }


def create_entity(client, auth: dict, key: str):
    response = client.post(
        "/api/v1/kg/entities",
        headers=headers(auth),
        json={"canonical_key": key, "kind": "Asset", "name": key},
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_source(client, auth: dict, key: str):
    response = client.post(
        "/api/v1/kg/sources",
        headers=headers(auth),
        json={
            "canonical_key": key,
            "name": key,
            "source_type": "inspection",
            "authority_score": 0.9,
            "last_checked_at": utcnow().isoformat(),
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def create_literal_assertion(client, auth: dict, entity_id: str, source_id: str, *, verified_at=None):
    payload = {
        "subject_entity_id": entity_id,
        "predicate": "status",
        "literal_value": "active",
        "source_id": source_id,
        "confidence": 0.95,
    }
    if verified_at:
        payload["verified_at"] = verified_at.isoformat()
    response = client.post("/api/v1/kg/assertions", headers=headers(auth), json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def seed_public_scalar(suffix: str):
    with SessionLocal() as db:
        source, _ = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"source:review:{suffix}",
            name=f"Review source {suffix}",
            source_type="official",
            url=f"https://example.com/{suffix}",
            authority_score=1.0,
            status="active",
            last_checked_at=utcnow(),
        )
        entity, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key=f"problem:review-{suffix}",
            kind="Problem",
            name=f"Review Problem {suffix}",
            is_public=True,
        )
        assertion, _ = upsert_assertion(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            subject_entity_id=entity.id,
            predicate="hasRiskLevel",
            literal_value="red",
            source_id=source.id,
            confidence=0.97,
            is_public=True,
            verified_at=utcnow(),
            evidence={"fixture": suffix},
        )
        db.commit()
        return {
            "source_id": source.id,
            "entity_id": entity.id,
            "assertion_id": assertion.id,
            "entity_key": entity.canonical_key,
        }


def test_scalar_jsonld_keeps_value_confidence_verification_and_source(client):
    fixture = seed_public_scalar("scalar-provenance")
    response = client.get(f"/api/v1/kg/public/entities/{fixture['entity_key']}/jsonld")
    assert response.status_code == 200, response.text
    claim = response.json()["hasRiskLevel"]
    assert claim["value"] == "red"
    assert claim["confidence"] == 0.97
    assert claim["verifiedAt"]
    assert claim["source"] == "https://example.com/scalar-provenance"


def test_health_uses_latest_verification_instead_of_all_historical_failures(client):
    auth = register(client, "kg-review-latest@example.com", "KG Review Latest")
    entity = create_entity(client, auth, "asset:review-latest")
    source = create_source(client, auth, "source:review-latest")
    assertion = create_literal_assertion(client, auth, entity["id"], source["id"], verified_at=utcnow())

    first = client.post(
        "/api/v1/kg/verifications",
        headers=headers(auth),
        json={
            "source_id": source["id"],
            "target_assertion_id": assertion["id"],
            "status": "unreachable",
            "checked_at": (utcnow() - timedelta(hours=1)).isoformat(),
        },
    )
    assert first.status_code == 201, first.text
    recovered = client.post(
        "/api/v1/kg/verifications",
        headers=headers(auth),
        json={
            "source_id": source["id"],
            "target_assertion_id": assertion["id"],
            "status": "verified",
            "checked_at": utcnow().isoformat(),
        },
    )
    assert recovered.status_code == 201, recovered.text

    health = client.get("/api/v1/kg/health", headers=headers(auth))
    assert health.status_code == 200, health.text
    assert health.json()["verification_failures"] == 0
    assert health.json()["unhealthy_sources"] == 0


def test_tenant_verification_cannot_mutate_global_source_or_assertion(client):
    fixture = seed_public_scalar("global-read-only")
    auth = register(client, "kg-review-global@example.com", "KG Review Global")

    with SessionLocal() as db:
        source = db.get(KnowledgeSource, fixture["source_id"])
        assertion = db.get(KnowledgeAssertion, fixture["assertion_id"])
        before = {
            "source_status": source.status,
            "source_hash": source.content_hash,
            "source_checked": source.last_checked_at,
            "assertion_status": assertion.status,
            "assertion_verified": assertion.verified_at,
        }

    response = client.post(
        "/api/v1/kg/verifications",
        headers=headers(auth),
        json={
            "source_id": fixture["source_id"],
            "target_assertion_id": fixture["assertion_id"],
            "status": "changed",
            "content_hash": "b" * 64,
            "details": {"tenant_observation": True},
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["details"]["global_target_read_only"] is True

    with SessionLocal() as db:
        source = db.get(KnowledgeSource, fixture["source_id"])
        assertion = db.get(KnowledgeAssertion, fixture["assertion_id"])
        assert source.status == before["source_status"]
        assert source.content_hash == before["source_hash"]
        assert source.last_checked_at == before["source_checked"]
        assert assertion.status == before["assertion_status"]
        assert assertion.verified_at == before["assertion_verified"]


def test_public_bundle_does_not_leak_hidden_object_entity(client):
    with SessionLocal() as db:
        source, _ = upsert_source(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="source:review:hidden-edge",
            name="Hidden edge source",
            source_type="official",
            url="https://example.com/hidden-edge",
            authority_score=1.0,
            status="active",
        )
        visible, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="entity:review-visible",
            kind="Problem",
            name="Visible review entity",
            is_public=True,
        )
        hidden, _ = upsert_entity(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            canonical_key="entity:review-hidden",
            kind="InternalEntity",
            name="Hidden review entity",
            is_public=False,
        )
        upsert_assertion(
            db,
            scope_key=GLOBAL_SCOPE,
            organization_id=None,
            subject_entity_id=visible.id,
            predicate="derivedFrom",
            object_entity_id=hidden.id,
            source_id=source.id,
            confidence=1.0,
            is_public=True,
            verified_at=utcnow(),
        )
        db.commit()

    response = client.get("/api/v1/kg/public/entities/entity:review-visible")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["assertions"] == []
    assert payload["included_entities"] == []
