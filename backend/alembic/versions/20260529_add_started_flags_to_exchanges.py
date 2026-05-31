"""Add started flags to exchanges

Revision ID: 20260529_add_started_flags
Revises: 20260529_add_is_fraudulent
Create Date: 2026-05-29 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260529_add_started_flags"
down_revision: Union[str, None] = "20260529_add_is_fraudulent"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "exchanges",
        sa.Column("started_by_initiator", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "exchanges",
        sa.Column("started_by_partner", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "exchanges",
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("exchanges", "started_by_initiator")
    op.drop_column("exchanges", "started_by_partner")
    op.drop_column("exchanges", "started_at")
