from __future__ import annotations

import hashlib
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, aliased

from .kg_models import KnowledgeAssertion, KnowledgeEntity, KnowledgeSource, KnowledgeVerificationRun
from .models import utcnow

GLOBAL_SCOPE = "global"
JSON_LD_CONTEXT: dict[str, Any] = {
    "@vocab": "https://schema.alo186.com/v1/",
    "name": "https://schema.org/name",
    "description": "https://schema.org/description",
    "url": {"@id": "https://schema.org/url", "@type": "@id"},
    "value": "https://schema.org/value",
    "partOf": {"@type": "@id"},
    "servedBy": {"@type": "@id"},
    "hasOfficialChannel": {"@type": "@id"},
    "routesTo": {"@type": "@id"},
    "locatedAt": {"@type": "@id"},
    "ownsAsset": {"@type": "@id"},
    "protectsLoad": {"@type": "@id"},
    "affectedBy": {"@type": "@id"},
    "generatedTask": {"@type": "@id"},
    "verifiedBy": {"@type": "@id"},
    "derivedFrom": {"@type": "@id"},
    "supersedes": {"@type": "@id"},
    "confidence": "https://schema.alo186.com/v1/confidence",
    "verifiedAt": {"@id": "https://schema.alo186.com/v1/verifiedAt", "@type": "https://schema.org/DateTime"},
    "source": {"@id": "https://schema.org/citation", "@type": "@id"},
}


def org_scope(organization_id: str) -> str:
    return f"org:{organization_id}"


def json_dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def json_loads(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return default


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def assertion_fingerprint(
    *,
    subject_entity_id: str,
    predicate: str,
    object_entity_id: str | None,
    literal_value: Any,
    source_id: str,
) -> str:
    payload = {
        "subject": subject_entity_id,
        "predicate": predicate,
        "object": object_entity_id,
        "literal": None if object_entity_id else literal_value,
        "source": source_id,
    }
    return hashlib.sha256(json_dumps(payload).encode("utf-8")).hexdigest()


def evidence_hash(value: Any) -> str:
    return hashlib.sha256(json_dumps(value).encode("utf-8")).hexdigest()


def entity_query_for_org(organization_id: str):
    return or_(
        KnowledgeEntity.scope_key == org_scope(organization_id),
        and_(KnowledgeEntity.scope_key == GLOBAL_SCOPE, KnowledgeEntity.is_public.is_(True)),
    )


def source_query_for_org(organization_id: str):
    return or_(
        KnowledgeSource.scope_key == org_scope(organization_id),
        KnowledgeSource.scope_key == GLOBAL_SCOPE,
    )


def assertion_query_for_org(organization_id: str):
    return or_(
        KnowledgeAssertion.scope_key == org_scope(organization_id),
        and_(KnowledgeAssertion.scope_key == GLOBAL_SCOPE, KnowledgeAssertion.is_public.is_(True)),
    )


def get_entity_for_org(db: Session, entity_id: str, organization_id: str) -> KnowledgeEntity | None:
    return db.scalar(
        select(KnowledgeEntity).where(
            KnowledgeEntity.id == entity_id,
            entity_query_for_org(organization_id),
        )
    )


def get_source_for_org(db: Session, source_id: str, organization_id: str) -> KnowledgeSource | None:
    return db.scalar(
        select(KnowledgeSource).where(
            KnowledgeSource.id == source_id,
            source_query_for_org(organization_id),
        )
    )


def serialize_entity(entity: KnowledgeEntity) -> dict[str, Any]:
    return {
        "id": entity.id,
        "scope_key": entity.scope_key,
        "organization_id": entity.organization_id,
        "canonical_key": entity.canonical_key,
        "kind": entity.kind,
        "name": entity.name,
        "description": entity.description,
        "properties": json_loads(entity.properties_json, {}),
        "is_public": entity.is_public,
        "status": entity.status,
        "created_at": entity.created_at,
        "updated_at": entity.updated_at,
    }


def serialize_source(source: KnowledgeSource) -> dict[str, Any]:
    return {
        "id": source.id,
        "scope_key": source.scope_key,
        "organization_id": source.organization_id,
        "canonical_key": source.canonical_key,
        "name": source.name,
        "source_type": source.source_type,
        "url": source.url,
        "authority_score": source.authority_score,
        "license_name": source.license_name,
        "status": source.status,
        "content_hash": source.content_hash,
        "last_checked_at": source.last_checked_at,
        "created_at": source.created_at,
        "updated_at": source.updated_at,
    }


def serialize_assertion(assertion: KnowledgeAssertion) -> dict[str, Any]:
    return {
        "id": assertion.id,
        "scope_key": assertion.scope_key,
        "organization_id": assertion.organization_id,
        "subject_entity_id": assertion.subject_entity_id,
        "predicate": assertion.predicate,
        "object_entity_id": assertion.object_entity_id,
        "literal_value": json_loads(assertion.literal_json, None),
        "source_id": assertion.source_id,
        "confidence": assertion.confidence,
        "status": assertion.status,
        "is_public": assertion.is_public,
        "valid_from": assertion.valid_from,
        "valid_to": assertion.valid_to,
        "verified_at": assertion.verified_at,
        "evidence_hash": assertion.evidence_hash,
        "properties": json_loads(assertion.properties_json, {}),
        "fingerprint": assertion.fingerprint,
        "created_at": assertion.created_at,
        "updated_at": assertion.updated_at,
    }


def upsert_entity(
    db: Session,
    *,
    scope_key: str,
    organization_id: str | None,
    canonical_key: str,
    kind: str,
    name: str,
    description: str | None = None,
    properties: dict[str, Any] | None = None,
    is_public: bool = False,
    status: str = "active",
) -> tuple[KnowledgeEntity, bool]:
    entity = db.scalar(
        select(KnowledgeEntity).where(
            KnowledgeEntity.scope_key == scope_key,
            KnowledgeEntity.canonical_key == canonical_key,
        )
    )
    created = entity is None
    if entity is None:
        entity = KnowledgeEntity(scope_key=scope_key, canonical_key=canonical_key)
        db.add(entity)
    entity.organization_id = organization_id
    entity.kind = kind
    entity.name = name
    entity.description = description
    entity.properties_json = json_dumps(properties or {})
    entity.is_public = bool(is_public)
    entity.status = status
    entity.updated_at = utcnow()
    db.flush()
    return entity, created


def upsert_source(
    db: Session,
    *,
    scope_key: str,
    organization_id: str | None,
    canonical_key: str,
    name: str,
    source_type: str = "web",
    url: str | None = None,
    authority_score: float = 0.5,
    license_name: str | None = None,
    status: str = "active",
    content_hash: str | None = None,
    last_checked_at: datetime | None = None,
) -> tuple[KnowledgeSource, bool]:
    source = db.scalar(
        select(KnowledgeSource).where(
            KnowledgeSource.scope_key == scope_key,
            KnowledgeSource.canonical_key == canonical_key,
        )
    )
    created = source is None
    if source is None:
        source = KnowledgeSource(scope_key=scope_key, canonical_key=canonical_key)
        db.add(source)
    source.organization_id = organization_id
    source.name = name
    source.source_type = source_type
    source.url = url
    source.authority_score = max(0.0, min(1.0, authority_score))
    source.license_name = license_name
    source.status = status
    source.content_hash = content_hash
    source.last_checked_at = last_checked_at
    source.updated_at = utcnow()
    db.flush()
    return source, created


def upsert_assertion(
    db: Session,
    *,
    scope_key: str,
    organization_id: str | None,
    subject_entity_id: str,
    predicate: str,
    source_id: str,
    object_entity_id: str | None = None,
    literal_value: Any = None,
    confidence: float = 1.0,
    status: str = "active",
    is_public: bool = False,
    valid_from: datetime | None = None,
    valid_to: datetime | None = None,
    verified_at: datetime | None = None,
    evidence: Any = None,
    properties: dict[str, Any] | None = None,
    created_by_user_id: str | None = None,
) -> tuple[KnowledgeAssertion, bool]:
    if (object_entity_id is None) == (literal_value is None):
        raise ValueError("Assertion tam olarak bir object_entity_id veya literal_value taşımalıdır.")
    fingerprint = assertion_fingerprint(
        subject_entity_id=subject_entity_id,
        predicate=predicate,
        object_entity_id=object_entity_id,
        literal_value=literal_value,
        source_id=source_id,
    )
    assertion = db.scalar(
        select(KnowledgeAssertion).where(
            KnowledgeAssertion.scope_key == scope_key,
            KnowledgeAssertion.fingerprint == fingerprint,
        )
    )
    created = assertion is None
    if assertion is None:
        assertion = KnowledgeAssertion(scope_key=scope_key, fingerprint=fingerprint)
        db.add(assertion)
    assertion.organization_id = organization_id
    assertion.subject_entity_id = subject_entity_id
    assertion.predicate = predicate
    assertion.object_entity_id = object_entity_id
    assertion.literal_json = None if object_entity_id else json_dumps(literal_value)
    assertion.source_id = source_id
    assertion.confidence = max(0.0, min(1.0, confidence))
    assertion.status = status
    assertion.is_public = bool(is_public)
    assertion.valid_from = valid_from
    assertion.valid_to = valid_to
    assertion.verified_at = verified_at
    assertion.evidence_hash = evidence_hash(evidence) if evidence is not None else None
    assertion.properties_json = json_dumps(properties or {})
    assertion.created_by_user_id = created_by_user_id
    assertion.updated_at = utcnow()
    db.flush()
    return assertion, created


def public_search(
    db: Session,
    *,
    query: str,
    kind: str | None = None,
    limit: int = 20,
) -> list[KnowledgeEntity]:
    pattern = f"%{query.strip()}%"
    stmt = select(KnowledgeEntity).where(
        KnowledgeEntity.scope_key == GLOBAL_SCOPE,
        KnowledgeEntity.is_public.is_(True),
        KnowledgeEntity.status == "active",
        or_(
            KnowledgeEntity.name.ilike(pattern),
            KnowledgeEntity.canonical_key.ilike(pattern),
            KnowledgeEntity.description.ilike(pattern),
        ),
    )
    if kind:
        stmt = stmt.where(KnowledgeEntity.kind == kind)
    return list(db.scalars(stmt.order_by(KnowledgeEntity.name).limit(max(1, min(limit, 100)))).all())


def entity_bundle(
    db: Session,
    *,
    entity: KnowledgeEntity,
    public_only: bool,
    organization_id: str | None = None,
    assertion_limit: int = 200,
) -> dict[str, Any]:
    filters = [KnowledgeAssertion.status == "active"]
    if public_only:
        filters.extend(
            [
                KnowledgeAssertion.scope_key == GLOBAL_SCOPE,
                KnowledgeAssertion.is_public.is_(True),
            ]
        )
    elif organization_id:
        filters.append(assertion_query_for_org(organization_id))
    assertions = list(
        db.scalars(
            select(KnowledgeAssertion)
            .where(
                or_(
                    KnowledgeAssertion.subject_entity_id == entity.id,
                    KnowledgeAssertion.object_entity_id == entity.id,
                ),
                *filters,
            )
            .order_by(KnowledgeAssertion.predicate, KnowledgeAssertion.created_at)
            .limit(max(1, min(assertion_limit, 500)))
        ).all()
    )
    entity_ids = {
        item
        for assertion in assertions
        for item in (assertion.subject_entity_id, assertion.object_entity_id)
        if item
    }
    source_ids = {assertion.source_id for assertion in assertions}
    entity_stmt = select(KnowledgeEntity).where(KnowledgeEntity.id.in_(entity_ids))
    source_stmt = select(KnowledgeSource).where(KnowledgeSource.id.in_(source_ids))
    if public_only:
        entity_stmt = entity_stmt.where(
            KnowledgeEntity.scope_key == GLOBAL_SCOPE,
            KnowledgeEntity.is_public.is_(True),
        )
        source_stmt = source_stmt.where(KnowledgeSource.scope_key == GLOBAL_SCOPE)
    elif organization_id:
        entity_stmt = entity_stmt.where(entity_query_for_org(organization_id))
        source_stmt = source_stmt.where(source_query_for_org(organization_id))
    entities = {item.id: item for item in db.scalars(entity_stmt).all()} if entity_ids else {}
    sources = {item.id: item for item in db.scalars(source_stmt).all()} if source_ids else {}
    visible_assertions = [
        item
        for item in assertions
        if item.subject_entity_id in entities
        and (item.object_entity_id is None or item.object_entity_id in entities)
        and item.source_id in sources
    ]
    return {
        "entity": serialize_entity(entity),
        "assertions": [serialize_assertion(item) for item in visible_assertions],
        "included_entities": [serialize_entity(item) for key, item in entities.items() if key != entity.id],
        "sources": [serialize_source(item) for item in sources.values()],
    }


def to_jsonld(bundle: dict[str, Any], *, public_base_url: str) -> dict[str, Any]:
    entity = bundle["entity"]
    included = {item["id"]: item for item in bundle.get("included_entities", [])}
    sources = {item["id"]: item for item in bundle.get("sources", [])}
    graph_id = f"{public_base_url.rstrip('/')}/kg/{quote(entity['canonical_key'], safe=':-._~')}"
    predicates: dict[str, list[Any]] = defaultdict(list)
    for assertion in bundle.get("assertions", []):
        if assertion["subject_entity_id"] != entity["id"]:
            continue
        if assertion["object_entity_id"]:
            target = included.get(assertion["object_entity_id"], {})
            value: dict[str, Any] = {
                "@id": f"{public_base_url.rstrip('/')}/kg/{quote(target.get('canonical_key', assertion['object_entity_id']), safe=':-._~')}",
                "@type": target.get("kind"),
                "name": target.get("name"),
            }
        else:
            literal = assertion["literal_value"]
            value = dict(literal) if isinstance(literal, dict) else {"value": literal}
        source = sources.get(assertion["source_id"])
        value["confidence"] = assertion["confidence"]
        if assertion["verified_at"]:
            value["verifiedAt"] = assertion["verified_at"]
        if source and source.get("url"):
            value["source"] = source["url"]
        predicates[assertion["predicate"]].append(value)
    document: dict[str, Any] = {
        "@context": JSON_LD_CONTEXT,
        "@id": graph_id,
        "@type": entity["kind"],
        "name": entity["name"],
        "description": entity["description"],
        **entity.get("properties", {}),
    }
    for predicate, values in predicates.items():
        document[predicate] = values[0] if len(values) == 1 else values
    return document


def _edge_rows(
    db: Session,
    *,
    public_only: bool,
    organization_id: str | None,
    limit: int,
) -> list[KnowledgeAssertion]:
    stmt = select(KnowledgeAssertion).where(
        KnowledgeAssertion.status == "active",
        KnowledgeAssertion.object_entity_id.is_not(None),
    )
    if public_only:
        subject = aliased(KnowledgeEntity)
        object_entity = aliased(KnowledgeEntity)
        stmt = (
            stmt.join(subject, subject.id == KnowledgeAssertion.subject_entity_id)
            .join(object_entity, object_entity.id == KnowledgeAssertion.object_entity_id)
            .where(
                KnowledgeAssertion.scope_key == GLOBAL_SCOPE,
                KnowledgeAssertion.is_public.is_(True),
                subject.scope_key == GLOBAL_SCOPE,
                subject.is_public.is_(True),
                object_entity.scope_key == GLOBAL_SCOPE,
                object_entity.is_public.is_(True),
            )
        )
    elif organization_id:
        stmt = stmt.where(assertion_query_for_org(organization_id))
    return list(db.scalars(stmt.limit(max(1, min(limit, 5_000)))).all())


def find_path(
    db: Session,
    *,
    start_entity_id: str,
    end_entity_id: str,
    public_only: bool,
    organization_id: str | None = None,
    max_depth: int = 4,
    edge_limit: int = 2_000,
) -> dict[str, Any] | None:
    max_depth = max(1, min(max_depth, 6))
    edges = _edge_rows(
        db,
        public_only=public_only,
        organization_id=organization_id,
        limit=edge_limit,
    )
    adjacency: dict[str, list[tuple[str, KnowledgeAssertion]]] = defaultdict(list)
    for edge in edges:
        if edge.object_entity_id:
            adjacency[edge.subject_entity_id].append((edge.object_entity_id, edge))
            adjacency[edge.object_entity_id].append((edge.subject_entity_id, edge))
    queue = deque([(start_entity_id, [])])
    visited = {start_entity_id}
    while queue:
        node, path = queue.popleft()
        if node == end_entity_id:
            ids = {start_entity_id, end_entity_id}
            for item in path:
                ids.add(item["from"])
                ids.add(item["to"])
            entity_stmt = select(KnowledgeEntity).where(KnowledgeEntity.id.in_(ids))
            if public_only:
                entity_stmt = entity_stmt.where(
                    KnowledgeEntity.scope_key == GLOBAL_SCOPE,
                    KnowledgeEntity.is_public.is_(True),
                )
            elif organization_id:
                entity_stmt = entity_stmt.where(entity_query_for_org(organization_id))
            entities = {item.id: serialize_entity(item) for item in db.scalars(entity_stmt).all()}
            if set(ids) != set(entities):
                return None
            return {"depth": len(path), "path": path, "entities": list(entities.values())}
        if len(path) >= max_depth:
            continue
        for neighbor, assertion in adjacency.get(node, []):
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append(
                (
                    neighbor,
                    path
                    + [
                        {
                            "assertion_id": assertion.id,
                            "predicate": assertion.predicate,
                            "from": node,
                            "to": neighbor,
                            "confidence": assertion.confidence,
                        }
                    ],
                )
            )
    return None


def graph_health(
    db: Session,
    *,
    public_only: bool,
    organization_id: str | None = None,
    stale_days: int = 30,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max(1, stale_days))
    entity_stmt = select(KnowledgeEntity)
    assertion_stmt = select(KnowledgeAssertion)
    source_stmt = select(KnowledgeSource)
    verification_stmt = select(KnowledgeVerificationRun)
    if public_only:
        entity_stmt = entity_stmt.where(
            KnowledgeEntity.scope_key == GLOBAL_SCOPE,
            KnowledgeEntity.is_public.is_(True),
        )
        assertion_stmt = assertion_stmt.where(
            KnowledgeAssertion.scope_key == GLOBAL_SCOPE,
            KnowledgeAssertion.is_public.is_(True),
        )
        source_stmt = source_stmt.where(KnowledgeSource.scope_key == GLOBAL_SCOPE)
        verification_stmt = verification_stmt.where(KnowledgeVerificationRun.scope_key == GLOBAL_SCOPE)
    elif organization_id:
        entity_stmt = entity_stmt.where(entity_query_for_org(organization_id))
        assertion_stmt = assertion_stmt.where(assertion_query_for_org(organization_id))
        source_stmt = source_stmt.where(source_query_for_org(organization_id))
        verification_stmt = verification_stmt.where(
            or_(
                KnowledgeVerificationRun.scope_key == org_scope(organization_id),
                KnowledgeVerificationRun.scope_key == GLOBAL_SCOPE,
            )
        )
    entities = list(db.scalars(entity_stmt).all())
    assertions = list(db.scalars(assertion_stmt).all())
    sources = list(db.scalars(source_stmt).all())
    verifications = list(db.scalars(verification_stmt).all())
    linked_ids = {
        item
        for assertion in assertions
        for item in (assertion.subject_entity_id, assertion.object_entity_id)
        if item
    }
    active_assertions = [item for item in assertions if item.status == "active"]
    stale = [
        item
        for item in active_assertions
        if item.verified_at is None or _aware(item.verified_at) < cutoff
    ]
    expired = [
        item
        for item in active_assertions
        if item.valid_to is not None and _aware(item.valid_to) < now
    ]
    low_confidence = [item for item in active_assertions if item.confidence < 0.5]
    source_unhealthy = [item for item in sources if item.status not in {"active", "ok"}]
    latest_verifications: dict[tuple[str, str | None, str | None], KnowledgeVerificationRun] = {}
    for item in verifications:
        key = (item.source_id, item.target_entity_id, item.target_assertion_id)
        current = latest_verifications.get(key)
        if current is None or _aware(item.checked_at) > _aware(current.checked_at):
            latest_verifications[key] = item
    verification_failures = [
        item
        for item in latest_verifications.values()
        if item.status not in {"ok", "unchanged", "verified"}
    ]
    literal_groups: dict[tuple[str, str], set[str]] = defaultdict(set)
    for item in active_assertions:
        if item.literal_json is not None:
            literal_groups[(item.subject_entity_id, item.predicate)].add(item.literal_json)
    conflicts = [key for key, values in literal_groups.items() if len(values) > 1]
    orphan_count = sum(1 for item in entities if item.id not in linked_ids)
    penalty = (
        min(len(stale), 50) * 0.6
        + orphan_count * 0.8
        + len(low_confidence) * 1.0
        + len(expired) * 1.2
        + len(conflicts) * 3.0
        + len(source_unhealthy) * 2.0
        + len(verification_failures) * 1.5
    )
    score = max(0, round(100 - penalty, 1))
    return {
        "score": score,
        "entities": len(entities),
        "assertions": len(assertions),
        "active_assertions": len(active_assertions),
        "sources": len(sources),
        "stale_assertions": len(stale),
        "orphan_entities": orphan_count,
        "low_confidence_assertions": len(low_confidence),
        "expired_assertions": len(expired),
        "conflicting_literal_claims": len(conflicts),
        "unhealthy_sources": len(source_unhealthy),
        "verification_failures": len(verification_failures),
        "stale_after_days": max(1, stale_days),
        "generated_at": now,
    }


def refresh_graph_metrics(metrics: Any, health: dict[str, Any], *, scope: str) -> None:
    if not hasattr(metrics, "set_gauge"):
        return
    labels = {"scope": scope}
    metrics.set_gauge("alo186_kg_health_score", health["score"], labels=labels)
    metrics.set_gauge("alo186_kg_entities", health["entities"], labels=labels)
    metrics.set_gauge("alo186_kg_assertions", health["assertions"], labels=labels)
    metrics.set_gauge("alo186_kg_stale_assertions", health["stale_assertions"], labels=labels)
    metrics.set_gauge("alo186_kg_orphan_entities", health["orphan_entities"], labels=labels)
    metrics.set_gauge("alo186_kg_conflicting_claims", health["conflicting_literal_claims"], labels=labels)
