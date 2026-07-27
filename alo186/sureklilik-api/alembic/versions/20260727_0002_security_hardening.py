"""Kimlik, MFA, outbox, plan ve KVKK sertleştirmesi.

Revision ID: 20260727_0002
Revises: 20260727_0001
Create Date: 2026-07-27
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20260727_0002"
down_revision = "20260727_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("is_email_verified", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.add_column(sa.Column("email_verified_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("token_version", sa.Integer(), nullable=False, server_default="1"))
        batch.add_column(sa.Column("failed_login_count", sa.Integer(), nullable=False, server_default="0"))
        batch.add_column(sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()))
        batch.add_column(sa.Column("mfa_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch.add_column(sa.Column("mfa_secret_ciphertext", sa.Text(), nullable=True))
        batch.add_column(sa.Column("mfa_recovery_codes_json", sa.Text(), nullable=True))
        batch.add_column(sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("deletion_execute_after", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("organizations") as batch:
        batch.add_column(sa.Column("subscription_status", sa.String(length=40), nullable=False, server_default="trial"))
        batch.add_column(sa.Column("plan_expires_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch.add_column(sa.Column("deletion_requested_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("deletion_execute_after", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("memberships") as batch:
        batch.add_column(sa.Column("notify_incidents", sa.Boolean(), nullable=False, server_default=sa.true()))

    with op.batch_alter_table("asset_tests") as batch:
        batch.alter_column("created_by_user_id", existing_type=sa.String(length=36), nullable=True)
    with op.batch_alter_table("incidents") as batch:
        batch.alter_column("created_by_user_id", existing_type=sa.String(length=36), nullable=True)
    with op.batch_alter_table("audit_logs") as batch:
        batch.alter_column("user_id", existing_type=sa.String(length=36), nullable=True)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("token_version", sa.Integer(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column("user_agent_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])

    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("purpose", sa.String(length=40), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("request_ip_hash", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_auth_tokens_user_id", "auth_tokens", ["user_id"])
    op.create_index("ix_auth_tokens_purpose", "auth_tokens", ["purpose"])
    op.create_index("ix_auth_tokens_token_hash", "auth_tokens", ["token_hash"], unique=True)
    op.create_index("ix_auth_tokens_expires_at", "auth_tokens", ["expires_at"])

    op.create_table(
        "email_outbox",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("organization_id", sa.String(length=36), nullable=True),
        sa.Column("to_email", sa.String(length=320), nullable=False),
        sa.Column("template", sa.String(length=80), nullable=False),
        sa.Column("subject", sa.String(length=240), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_email_outbox_user_id", "email_outbox", ["user_id"])
    op.create_index("ix_email_outbox_organization_id", "email_outbox", ["organization_id"])
    op.create_index("ix_email_outbox_to_email", "email_outbox", ["to_email"])
    op.create_index("ix_email_outbox_status", "email_outbox", ["status"])
    op.create_index("ix_email_outbox_available_at", "email_outbox", ["available_at"])

    with op.batch_alter_table("users") as batch:
        batch.alter_column("is_email_verified", server_default=sa.false())


def downgrade() -> None:
    op.drop_table("email_outbox")
    op.drop_table("auth_tokens")
    op.drop_table("auth_sessions")

    with op.batch_alter_table("audit_logs") as batch:
        batch.alter_column("user_id", existing_type=sa.String(length=36), nullable=False)
    with op.batch_alter_table("incidents") as batch:
        batch.alter_column("created_by_user_id", existing_type=sa.String(length=36), nullable=False)
    with op.batch_alter_table("asset_tests") as batch:
        batch.alter_column("created_by_user_id", existing_type=sa.String(length=36), nullable=False)

    with op.batch_alter_table("memberships") as batch:
        batch.drop_column("notify_incidents")

    with op.batch_alter_table("organizations") as batch:
        for column in (
            "deleted_at",
            "deletion_execute_after",
            "deletion_requested_at",
            "is_active",
            "plan_expires_at",
            "subscription_status",
        ):
            batch.drop_column(column)

    with op.batch_alter_table("users") as batch:
        for column in (
            "deleted_at",
            "deletion_execute_after",
            "deletion_requested_at",
            "mfa_recovery_codes_json",
            "mfa_secret_ciphertext",
            "mfa_enabled",
            "password_changed_at",
            "last_login_at",
            "locked_until",
            "failed_login_count",
            "token_version",
            "email_verified_at",
            "is_email_verified",
        ):
            batch.drop_column(column)
