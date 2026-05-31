"""Make skills nullable in exchange_participants

Revision ID: 20260529_make_skills_nullable
Revises: 20260529_add_started_flags
Create Date: 2026-05-29 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260529_make_skills_nullable"
down_revision: Union[str, None] = "20260529_add_started_flags"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "exchange_participants",
        "gives_skill_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "exchange_participants",
        "gets_skill_id",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "exchange_participants",
        "gives_skill_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "exchange_participants",
        "gets_skill_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
