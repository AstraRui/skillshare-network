"""Add completion confirmations and review constraints.

Revision ID: c7d9e4f1a2b3
Revises: a1b2c3d4e5f6
Create Date: 2026-05-12
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "c7d9e4f1a2b3"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "exchanges",
        sa.Column("completed_by_initiator", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "exchanges",
        sa.Column("completed_by_partner", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_unique_constraint(
        "uq_review_exchange_reviewer", "reviews", ["exchange_id", "reviewer_id"]
    )
    op.create_check_constraint("ck_review_rating_range", "reviews", "rating >= 1 AND rating <= 5")


def downgrade() -> None:
    op.drop_constraint("ck_review_rating_range", "reviews", type_="check")
    op.drop_constraint("uq_review_exchange_reviewer", "reviews", type_="unique")
    op.drop_column("exchanges", "completed_by_partner")
    op.drop_column("exchanges", "completed_by_initiator")
