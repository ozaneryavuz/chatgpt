"""Knowledge Graph verification status index.

Revision ID: 20260728_0005
Revises: 20260728_0004
Create Date: 2026-07-28
"""

from __future__ import annotations

from alembic import op

revision = "20260728_0005"
down_revision = "20260728_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_kg_verification_runs_status",
        "kg_verification_runs",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_kg_verification_runs_status", table_name="kg_verification_runs")
