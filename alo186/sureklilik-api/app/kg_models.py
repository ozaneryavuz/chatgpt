from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Float, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base
from .models import new_id, utcnow


class KnowledgeEntity(Base):
    __tablename__ = "kg_entities"
    __table_args__ = (
        UniqueConstraint("scope_key", "canonical_key", name="uq_kg_entity_scope_canonical"),
        Index("ix_kg_entities_scope_kind_name", "scope_key", "kind", "name"),
        Index("ix_kg_entities_public_kind", "is_public", "kind"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    scope_key: Mapped[str] = mapped_column(String(90), default="global", index=True)
    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    canonical_key: Mapped[str] = mapped_column(String(260))
    kind: Mapped[str] = mapped_column(String(90), index=True)
    name: Mapped[str] = mapped_column(String(260), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    properties_json: Mapped[str] = mapped_column(Text, default="{}")
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class KnowledgeSource(Base):
    __tablename__ = "kg_sources"
    __table_args__ = (
        UniqueConstraint("scope_key", "canonical_key", name="uq_kg_source_scope_canonical"),
        Index("ix_kg_sources_scope_status", "scope_key", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    scope_key: Mapped[str] = mapped_column(String(90), default="global", index=True)
    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    canonical_key: Mapped[str] = mapped_column(String(260))
    name: Mapped[str] = mapped_column(String(260))
    source_type: Mapped[str] = mapped_column(String(80), default="web")
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    authority_score: Mapped[float] = mapped_column(Float, default=0.5)
    license_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_checked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class KnowledgeAssertion(Base):
    __tablename__ = "kg_assertions"
    __table_args__ = (
        UniqueConstraint("scope_key", "fingerprint", name="uq_kg_assertion_scope_fingerprint"),
        CheckConstraint(
            "(object_entity_id IS NOT NULL AND literal_json IS NULL) OR "
            "(object_entity_id IS NULL AND literal_json IS NOT NULL)",
            name="ck_kg_assertion_object_xor_literal",
        ),
        Index("ix_kg_assertions_subject_predicate", "subject_entity_id", "predicate"),
        Index("ix_kg_assertions_object_predicate", "object_entity_id", "predicate"),
        Index("ix_kg_assertions_scope_status", "scope_key", "status"),
        Index("ix_kg_assertions_public_status", "is_public", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    scope_key: Mapped[str] = mapped_column(String(90), default="global", index=True)
    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    subject_entity_id: Mapped[str] = mapped_column(
        ForeignKey("kg_entities.id", ondelete="CASCADE"), index=True
    )
    predicate: Mapped[str] = mapped_column(String(120), index=True)
    object_entity_id: Mapped[str | None] = mapped_column(
        ForeignKey("kg_entities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    literal_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_id: Mapped[str] = mapped_column(
        ForeignKey("kg_sources.id", ondelete="RESTRICT"), index=True
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    status: Mapped[str] = mapped_column(String(30), default="active", index=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    valid_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    evidence_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    properties_json: Mapped[str] = mapped_column(Text, default="{}")
    fingerprint: Mapped[str] = mapped_column(String(64))
    created_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class KnowledgeVerificationRun(Base):
    __tablename__ = "kg_verification_runs"
    __table_args__ = (
        Index("ix_kg_verification_scope_checked", "scope_key", "checked_at"),
        Index("ix_kg_verification_source_status", "source_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    scope_key: Mapped[str] = mapped_column(String(90), default="global", index=True)
    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True
    )
    source_id: Mapped[str] = mapped_column(
        ForeignKey("kg_sources.id", ondelete="CASCADE"), index=True
    )
    target_entity_id: Mapped[str | None] = mapped_column(
        ForeignKey("kg_entities.id", ondelete="CASCADE"), nullable=True, index=True
    )
    target_assertion_id: Mapped[str | None] = mapped_column(
        ForeignKey("kg_assertions.id", ondelete="CASCADE"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(String(30), index=True)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    duration_ms: Mapped[int | None] = mapped_column(nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
