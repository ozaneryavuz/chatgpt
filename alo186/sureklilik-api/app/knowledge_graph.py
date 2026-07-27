from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .audit import write_audit
from .config import settings
from .deps import OrgContext, get_db, get_org_context, require_roles
from .kg_models import KnowledgeAssertion, KnowledgeEntity, KnowledgeSource, KnowledgeVerificationRun
from .kg_service import (
    GLOBAL_SCOPE,
    assertion_query_for_org,
    entity_bundle,
    entity_query_for_org,
    find_path,
    get_entity_for_org,
    get_source_for_org,
    graph_health,
    json_dumps,
    org_scope,
    public_search,
    refresh_graph_metrics,
    serialize_assertion,
    serialize_entity,
    serialize_source,
    to_jsonld,
    upsert_assertion,
    upsert_entity,
    upsert_source,
)
from .models import Role, utcnow
from .observability import metrics

router = APIRouter(prefix="/api/v1/kg", tags=["knowledge-graph"])


class KgModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EntityCreate(KgModel):
    canonical_key: str = Field(min_length=3, max_length=260, pattern=r"^[A-Za-z0-9._:-]+$")
    kind: str = Field(min_length=2, max_length=90, pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    name: str = Field(min_length=2, max_length=260)
    description: str | None = Field(default=None, max_length=4_000)
    properties: dict[str, Any] = Field(default_factory=dict)


class EntityPatch(KgModel):
    name: str | None = Field(default=None, min_length=2, max_length=260)
    description: str | None = Field(default=None, max_length=4_000)
    properties: dict[str, Any] | None = None
    status: Literal["active", "deprecated", "retired"] | None = None


class SourceCreate(KgModel):
    canonical_key: str = Field(min_length=3, max_length=260, pattern=r"^[A-Za-z0-9._:-]+$")
    name: str = Field(min_length=2, max_length=260)
    source_type: str = Field(default="web", min_length=2, max_length=80)
    url: HttpUrl | None = None
    authority_score: float = Field(default=0.5, ge=0, le=1)
    license_name: str | None = Field(default=None, max_length=160)
    content_hash: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    last_checked_at: datetime | None = None


class AssertionCreate(KgModel):
    subject_entity_id: str = Field(min_length=36, max_length=36)
    predicate: str = Field(min_length=2, max_length=120, pattern=r"^[A-Za-z][A-Za-z0-9_-]*$")
    object_entity_id: str | None = Field(default=None, min_length=36, max_length=36)
    literal_value: Any = None
    source_id: str = Field(min_length=36, max_length=36)
    confidence: float = Field(default=1.0, ge=0, le=1)
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    verified_at: datetime | None = None
    evidence: Any = None
    properties: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def exactly_one_object(self):
        if (self.object_entity_id is None) == (self.literal_value is None):
            raise ValueError("Tam olarak bir object_entity_id veya literal_value girilmelidir.")
        if self.valid_from and self.valid_to and self.valid_to <= self.valid_from:
            raise ValueError("valid_to, valid_from sonrasında olmalıdır.")
        return self


class AssertionPatch(KgModel):
    confidence: float | None = Field(default=None, ge=0, le=1)
    status: Literal["active", "disputed", "superseded", "expired", "retired"] | None = None
    verified_at: datetime | None = None
    valid_to: datetime | None = None
    properties: dict[str, Any] | None = None


class VerificationCreate(KgModel):
    source_id: str = Field(min_length=36, max_length=36)
    target_entity_id: str | None = Field(default=None, min_length=36, max_length=36)
    target_assertion_id: str | None = Field(default=None, min_length=36, max_length=36)
    status: Literal["ok", "unchanged", "verified", "changed", "unreachable", "invalid", "error"]
    checked_at: datetime | None = None
    duration_ms: int | None = Field(default=None, ge=0, le=600_000)
    content_hash: str | None = Field(default=None, pattern=r"^[a-fA-F0-9]{64}$")
    details: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def one_target_at_most(self):
        if self.target_entity_id and self.target_assertion_id:
            raise ValueError("Aynı doğrulama hem entity hem assertion hedefleyemez.")
        return self


def _public_entity(db: Session, canonical_key: str) -> KnowledgeEntity:
    entity = db.scalar(
        select(KnowledgeEntity).where(
            KnowledgeEntity.scope_key == GLOBAL_SCOPE,
            KnowledgeEntity.canonical_key == canonical_key,
            KnowledgeEntity.is_public.is_(True),
            KnowledgeEntity.status == "active",
        )
    )
    if not entity:
        raise HTTPException(status_code=404, detail="Knowledge Graph varlığı bulunamadı.")
    return entity


def _tenant_entity(db: Session, entity_id: str, context: OrgContext) -> KnowledgeEntity:
    entity = get_entity_for_org(db, entity_id, context.organization_id)
    if not entity:
        raise HTTPException(status_code=404, detail="Knowledge Graph varlığı bulunamadı.")
    return entity


def _tenant_assertion(db: Session, assertion_id: str, context: OrgContext) -> KnowledgeAssertion:
    assertion = db.scalar(
        select(KnowledgeAssertion).where(
            KnowledgeAssertion.id == assertion_id,
            assertion_query_for_org(context.organization_id),
        )
    )
    if not assertion:
        raise HTTPException(status_code=404, detail="Knowledge Graph iddiası bulunamadı.")
    return assertion


@router.get("/public/search")
def search_public_graph(
    q: str = Query(min_length=2, max_length=120),
    kind: str | None = Query(default=None, max_length=90),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = public_search(db, query=q, kind=kind, limit=limit)
    return {"query": q, "count": len(rows), "items": [serialize_entity(item) for item in rows]}


@router.get("/public/entities/{canonical_key}/jsonld")
def public_entity_jsonld(canonical_key: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    entity = _public_entity(db, canonical_key)
    bundle = entity_bundle(db, entity=entity, public_only=True)
    return to_jsonld(bundle, public_base_url=settings.public_base_url)


@router.get("/public/entities/{canonical_key}")
def public_entity(canonical_key: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    entity = _public_entity(db, canonical_key)
    return entity_bundle(db, entity=entity, public_only=True)


@router.get("/public/path")
def public_graph_path(
    from_key: str = Query(min_length=3, max_length=260),
    to_key: str = Query(min_length=3, max_length=260),
    max_depth: int = Query(default=4, ge=1, le=6),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    start = _public_entity(db, from_key)
    end = _public_entity(db, to_key)
    result = find_path(
        db,
        start_entity_id=start.id,
        end_entity_id=end.id,
        public_only=True,
        max_depth=max_depth,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Belirtilen derinlikte graph yolu bulunamadı.")
    return result


@router.get("/public/health")
def public_graph_health(
    stale_days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    health = graph_health(db, public_only=True, stale_days=stale_days)
    refresh_graph_metrics(metrics, health, scope="public")
    return health


@router.get("/entities")
def list_tenant_entities(
    q: str | None = Query(default=None, max_length=120),
    kind: str | None = Query(default=None, max_length=90),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0, le=50_000),
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    stmt = select(KnowledgeEntity).where(entity_query_for_org(context.organization_id))
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                KnowledgeEntity.name.ilike(pattern),
                KnowledgeEntity.canonical_key.ilike(pattern),
                KnowledgeEntity.description.ilike(pattern),
            )
        )
    if kind:
        stmt = stmt.where(KnowledgeEntity.kind == kind)
    rows = list(db.scalars(stmt.order_by(KnowledgeEntity.kind, KnowledgeEntity.name).offset(offset).limit(limit)).all())
    return {"count": len(rows), "items": [serialize_entity(item) for item in rows]}


@router.post("/entities", status_code=status.HTTP_201_CREATED)
def create_tenant_entity(
    payload: EntityCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    entity, created = upsert_entity(
        db,
        scope_key=org_scope(context.organization_id),
        organization_id=context.organization_id,
        canonical_key=payload.canonical_key,
        kind=payload.kind,
        name=payload.name,
        description=payload.description,
        properties=payload.properties,
        is_public=False,
    )
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.entity.upserted",
        entity_type="kg_entity",
        entity_id=entity.id,
        details={"canonical_key": entity.canonical_key, "created": created},
    )
    db.commit()
    return serialize_entity(entity)


@router.get("/entities/{entity_id}")
def get_tenant_entity(
    entity_id: str,
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    entity = _tenant_entity(db, entity_id, context)
    return entity_bundle(db, entity=entity, public_only=False, organization_id=context.organization_id)


@router.patch("/entities/{entity_id}")
def patch_tenant_entity(
    entity_id: str,
    payload: EntityPatch,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    entity = _tenant_entity(db, entity_id, context)
    if entity.scope_key == GLOBAL_SCOPE:
        raise HTTPException(status_code=403, detail="Global Knowledge Graph varlığı tenant API ile değiştirilemez.")
    values = payload.model_dump(exclude_unset=True)
    if "name" in values:
        entity.name = values["name"]
    if "description" in values:
        entity.description = values["description"]
    if "properties" in values:
        entity.properties_json = json_dumps(values["properties"] or {})
    if "status" in values:
        entity.status = values["status"]
    entity.updated_at = utcnow()
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.entity.updated",
        entity_type="kg_entity",
        entity_id=entity.id,
        details={"fields": sorted(values)},
    )
    db.commit()
    return serialize_entity(entity)


@router.delete("/entities/{entity_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def retire_tenant_entity(
    entity_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
) -> Response:
    entity = _tenant_entity(db, entity_id, context)
    if entity.scope_key == GLOBAL_SCOPE:
        raise HTTPException(status_code=403, detail="Global Knowledge Graph varlığı tenant API ile silinemez.")
    entity.status = "retired"
    entity.updated_at = utcnow()
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.entity.retired",
        entity_type="kg_entity",
        entity_id=entity.id,
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sources", status_code=status.HTTP_201_CREATED)
def create_tenant_source(
    payload: SourceCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    source, created = upsert_source(
        db,
        scope_key=org_scope(context.organization_id),
        organization_id=context.organization_id,
        canonical_key=payload.canonical_key,
        name=payload.name,
        source_type=payload.source_type,
        url=str(payload.url) if payload.url else None,
        authority_score=payload.authority_score,
        license_name=payload.license_name,
        content_hash=payload.content_hash,
        last_checked_at=payload.last_checked_at,
    )
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.source.upserted",
        entity_type="kg_source",
        entity_id=source.id,
        details={"canonical_key": source.canonical_key, "created": created},
    )
    db.commit()
    return serialize_source(source)


@router.post("/assertions", status_code=status.HTTP_201_CREATED)
def create_tenant_assertion(
    payload: AssertionCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    subject = _tenant_entity(db, payload.subject_entity_id, context)
    object_entity = _tenant_entity(db, payload.object_entity_id, context) if payload.object_entity_id else None
    source = get_source_for_org(db, payload.source_id, context.organization_id)
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge Graph kaynağı bulunamadı.")
    assertion, created = upsert_assertion(
        db,
        scope_key=org_scope(context.organization_id),
        organization_id=context.organization_id,
        subject_entity_id=subject.id,
        predicate=payload.predicate,
        object_entity_id=object_entity.id if object_entity else None,
        literal_value=payload.literal_value,
        source_id=source.id,
        confidence=payload.confidence,
        is_public=False,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        verified_at=payload.verified_at,
        evidence=payload.evidence,
        properties=payload.properties,
        created_by_user_id=context.user.id,
    )
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.assertion.upserted",
        entity_type="kg_assertion",
        entity_id=assertion.id,
        details={"predicate": assertion.predicate, "created": created},
    )
    db.commit()
    return serialize_assertion(assertion)


@router.patch("/assertions/{assertion_id}")
def patch_tenant_assertion(
    assertion_id: str,
    payload: AssertionPatch,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    assertion = _tenant_assertion(db, assertion_id, context)
    if assertion.scope_key == GLOBAL_SCOPE:
        raise HTTPException(status_code=403, detail="Global Knowledge Graph iddiası tenant API ile değiştirilemez.")
    values = payload.model_dump(exclude_unset=True)
    if "confidence" in values:
        assertion.confidence = values["confidence"]
    if "status" in values:
        assertion.status = values["status"]
    if "verified_at" in values:
        assertion.verified_at = values["verified_at"]
    if "valid_to" in values:
        assertion.valid_to = values["valid_to"]
    if "properties" in values:
        assertion.properties_json = json_dumps(values["properties"] or {})
    assertion.updated_at = utcnow()
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.assertion.updated",
        entity_type="kg_assertion",
        entity_id=assertion.id,
        details={"fields": sorted(values)},
    )
    db.commit()
    return serialize_assertion(assertion)


@router.delete("/assertions/{assertion_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def retire_tenant_assertion(
    assertion_id: str,
    context: OrgContext = Depends(require_roles(Role.admin)),
    db: Session = Depends(get_db),
) -> Response:
    assertion = _tenant_assertion(db, assertion_id, context)
    if assertion.scope_key == GLOBAL_SCOPE:
        raise HTTPException(status_code=403, detail="Global Knowledge Graph iddiası tenant API ile silinemez.")
    assertion.status = "retired"
    assertion.updated_at = utcnow()
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.assertion.retired",
        entity_type="kg_assertion",
        entity_id=assertion.id,
    )
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/entities/{entity_id}/neighbors")
def tenant_entity_neighbors(
    entity_id: str,
    limit: int = Query(default=200, ge=1, le=500),
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    entity = _tenant_entity(db, entity_id, context)
    return entity_bundle(
        db,
        entity=entity,
        public_only=False,
        organization_id=context.organization_id,
        assertion_limit=limit,
    )


@router.get("/path")
def tenant_graph_path(
    from_id: str = Query(min_length=36, max_length=36),
    to_id: str = Query(min_length=36, max_length=36),
    max_depth: int = Query(default=4, ge=1, le=6),
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    start = _tenant_entity(db, from_id, context)
    end = _tenant_entity(db, to_id, context)
    result = find_path(
        db,
        start_entity_id=start.id,
        end_entity_id=end.id,
        public_only=False,
        organization_id=context.organization_id,
        max_depth=max_depth,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Belirtilen derinlikte graph yolu bulunamadı.")
    return result


@router.post("/verifications", status_code=status.HTTP_201_CREATED)
def create_verification(
    payload: VerificationCreate,
    context: OrgContext = Depends(require_roles(Role.admin, Role.technician)),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    source = get_source_for_org(db, payload.source_id, context.organization_id)
    if not source:
        raise HTTPException(status_code=404, detail="Knowledge Graph kaynağı bulunamadı.")
    entity = _tenant_entity(db, payload.target_entity_id, context) if payload.target_entity_id else None
    assertion = _tenant_assertion(db, payload.target_assertion_id, context) if payload.target_assertion_id else None
    checked_at = payload.checked_at or utcnow()
    run = KnowledgeVerificationRun(
        scope_key=org_scope(context.organization_id),
        organization_id=context.organization_id,
        source_id=source.id,
        target_entity_id=entity.id if entity else None,
        target_assertion_id=assertion.id if assertion else None,
        status=payload.status,
        checked_at=checked_at,
        duration_ms=payload.duration_ms,
        content_hash=payload.content_hash,
        details_json=json.dumps(payload.details, ensure_ascii=False, sort_keys=True),
        created_by_user_id=context.user.id,
    )
    db.add(run)
    source.last_checked_at = checked_at
    source.status = "active" if payload.status in {"ok", "unchanged", "verified"} else payload.status
    if payload.content_hash:
        source.content_hash = payload.content_hash
    if assertion:
        assertion.verified_at = checked_at
        if payload.status in {"changed", "invalid", "error"}:
            assertion.status = "disputed"
    write_audit(
        db,
        organization_id=context.organization_id,
        user_id=context.user.id,
        action="kg.verification.created",
        entity_type="kg_verification",
        entity_id=run.id,
        details={"status": run.status, "source_id": source.id},
    )
    db.commit()
    return {
        "id": run.id,
        "source_id": run.source_id,
        "target_entity_id": run.target_entity_id,
        "target_assertion_id": run.target_assertion_id,
        "status": run.status,
        "checked_at": run.checked_at,
        "duration_ms": run.duration_ms,
        "content_hash": run.content_hash,
        "details": payload.details,
    }


@router.get("/health")
def tenant_graph_health(
    stale_days: int = Query(default=30, ge=1, le=365),
    context: OrgContext = Depends(get_org_context),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    health = graph_health(
        db,
        public_only=False,
        organization_id=context.organization_id,
        stale_days=stale_days,
    )
    refresh_graph_metrics(metrics, health, scope=f"org-{context.organization_id[:8]}")
    return health
