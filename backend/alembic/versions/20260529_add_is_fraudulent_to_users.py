"""Add is_fraudulent to users

Revision ID: 20260529_add_is_fraudulent
Revises: 20260519_fix_msg_constraint
Create Date: 2026-05-29 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260529_add_is_fraudulent"
down_revision: Union[str, None] = "20260519_fix_msg_constraint"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_fraudulent", sa.Boolean(), nullable=False, server_default="false")
    )


def downgrade() -> None:
    op.drop_column("users", "is_fraudulent")
