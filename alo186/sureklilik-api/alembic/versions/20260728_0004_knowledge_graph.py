"""ALO186 provenance-aware Knowledge Graph v1.

Revision ID: 20260728_0004
Revises: 20260728_0003
Create Date: 2026-07-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260728_0004"
down_revision = "20260728_0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kg_entities",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_key", sa.String(length=90), nullable=False, server_default="global"),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("canonical_key", sa.String(length=260), nullable=False),
        sa.Column("kind", sa.String(length=90), nullable=False),
        sa.Column("name", sa.String(length=260), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("properties_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_key", "canonical_key", name="uq_kg_entity_scope_canonical"),
    )
    op.create_index("ix_kg_entities_scope_key", "kg_entities", ["scope_key"])
    op.create_index("ix_kg_entities_organization_id", "kg_entities", ["organization_id"])
    op.create_index("ix_kg_entities_kind", "kg_entities", ["kind"])
    op.create_index("ix_kg_entities_name", "kg_entities", ["name"])
    op.create_index("ix_kg_entities_status", "kg_entities", ["status"])
    op.create_index("ix_kg_entities_is_public", "kg_entities", ["is_public"])
    op.create_index("ix_kg_entities_scope_kind_name", "kg_entities", ["scope_key", "kind", "name"])
    op.create_index("ix_kg_entities_public_kind", "kg_entities", ["is_public", "kind"])

    op.create_table(
        "kg_sources",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_key", sa.String(length=90), nullable=False, server_default="global"),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("canonical_key", sa.String(length=260), nullable=False),
        sa.Column("name", sa.String(length=260), nullable=False),
        sa.Column("source_type", sa.String(length=80), nullable=False, server_default="web"),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column("authority_score", sa.Float(), nullable=False, server_default="0.5"),
        sa.Column("license_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_key", "canonical_key", name="uq_kg_source_scope_canonical"),
    )
    op.create_index("ix_kg_sources_scope_key", "kg_sources", ["scope_key"])
    op.create_index("ix_kg_sources_organization_id", "kg_sources", ["organization_id"])
    op.create_index("ix_kg_sources_status", "kg_sources", ["status"])
    op.create_index("ix_kg_sources_scope_status", "kg_sources", ["scope_key", "status"])

    op.create_table(
        "kg_assertions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_key", sa.String(length=90), nullable=False, server_default="global"),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("subject_entity_id", sa.String(length=36), nullable=False),
        sa.Column("predicate", sa.String(length=120), nullable=False),
        sa.Column("object_entity_id", sa.String(length=36), nullable=True),
        sa.Column("literal_json", sa.Text(), nullable=True),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="active"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("evidence_hash", sa.String(length=64), nullable=True),
        sa.Column("properties_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "(object_entity_id IS NOT NULL AND literal_json IS NULL) OR "
            "(object_entity_id IS NULL AND literal_json IS NOT NULL)",
            name="ck_kg_assertion_object_xor_literal",
        ),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_entity_id"], ["kg_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["object_entity_id"], ["kg_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["kg_sources.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("scope_key", "fingerprint", name="uq_kg_assertion_scope_fingerprint"),
    )
    op.create_index("ix_kg_assertions_scope_key", "kg_assertions", ["scope_key"])
    op.create_index("ix_kg_assertions_organization_id", "kg_assertions", ["organization_id"])
    op.create_index("ix_kg_assertions_subject_entity_id", "kg_assertions", ["subject_entity_id"])
    op.create_index("ix_kg_assertions_predicate", "kg_assertions", ["predicate"])
    op.create_index("ix_kg_assertions_object_entity_id", "kg_assertions", ["object_entity_id"])
    op.create_index("ix_kg_assertions_source_id", "kg_assertions", ["source_id"])
    op.create_index("ix_kg_assertions_status", "kg_assertions", ["status"])
    op.create_index("ix_kg_assertions_is_public", "kg_assertions", ["is_public"])
    op.create_index("ix_kg_assertions_verified_at", "kg_assertions", ["verified_at"])
    op.create_index("ix_kg_assertions_subject_predicate", "kg_assertions", ["subject_entity_id", "predicate"])
    op.create_index("ix_kg_assertions_object_predicate", "kg_assertions", ["object_entity_id", "predicate"])
    op.create_index("ix_kg_assertions_scope_status", "kg_assertions", ["scope_key", "status"])
    op.create_index("ix_kg_assertions_public_status", "kg_assertions", ["is_public", "status"])

    op.create_table(
        "kg_verification_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("scope_key", sa.String(length=90), nullable=False, server_default="global"),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("source_id", sa.String(length=36), nullable=False),
        sa.Column("target_entity_id", sa.String(length=36), nullable=True),
        sa.Column("target_assertion_id", sa.String(length=36), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("content_hash", sa.String(length=64), nullable=True),
        sa.Column("details_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["source_id"], ["kg_sources.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_entity_id"], ["kg_entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_assertion_id"], ["kg_assertions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kg_verification_runs_scope_key", "kg_verification_runs", ["scope_key"])
    op.create_index("ix_kg_verification_runs_organization_id", "kg_verification_runs", ["organization_id"])
    op.create_index("ix_kg_verification_runs_source_id", "kg_verification_runs", ["source_id"])
    op.create_index("ix_kg_verification_runs_target_entity_id", "kg_verification_runs", ["target_entity_id"])
    op.create_index("ix_kg_verification_runs_target_assertion_id", "kg_verification_runs", ["target_assertion_id"])
    op.create_index("ix_kg_verification_scope_checked", "kg_verification_runs", ["scope_key", "checked_at"])
    op.create_index("ix_kg_verification_source_status", "kg_verification_runs", ["source_id", "status"])


def downgrade() -> None:
    op.drop_table("kg_verification_runs")
    op.drop_table("kg_assertions")
    op.drop_table("kg_sources")
    op.drop_table("kg_entities")
