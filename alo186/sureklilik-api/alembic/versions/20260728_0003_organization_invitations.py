"""Kuruluş davet tabanlı ekip onboarding'i.

Revision ID: 20260728_0003
Revises: 20260727_0002
Create Date: 2026-07-28
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260728_0003"
down_revision = "20260727_0002"
branch_labels = None
depends_on = None


def _role_type():
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        return postgresql.ENUM("admin", "technician", "viewer", name="role", create_type=False)
    return sa.Enum("admin", "technician", "viewer", name="role", native_enum=False)


def upgrade() -> None:
    op.create_table(
        "organization_invitations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("role", _role_type(), nullable=False),
        sa.Column("notify_incidents", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("invited_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("accepted_by_user_id", sa.String(length=36), nullable=True),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resend_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["accepted_by_user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(
        "ix_organization_invitations_organization_id",
        "organization_invitations",
        ["organization_id"],
    )
    op.create_index(
        "ix_organization_invitations_email",
        "organization_invitations",
        ["email"],
    )
    op.create_index(
        "ix_organization_invitations_token_hash",
        "organization_invitations",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "ix_organization_invitations_expires_at",
        "organization_invitations",
        ["expires_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_organization_invitations_expires_at", table_name="organization_invitations")
    op.drop_index("ix_organization_invitations_token_hash", table_name="organization_invitations")
    op.drop_index("ix_organization_invitations_email", table_name="organization_invitations")
    op.drop_index("ix_organization_invitations_organization_id", table_name="organization_invitations")
    op.drop_table("organization_invitations")
