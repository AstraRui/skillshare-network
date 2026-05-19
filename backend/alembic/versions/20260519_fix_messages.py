"""Add missing columns to messages

Revision ID: 20260519_fix_messages
Revises: 20260519_add_chats
Create Date: 2026-05-19 00:01:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_fix_messages"
down_revision: Union[str, None] = "20260519_add_chats"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("messages", sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("messages", "edited_at")
