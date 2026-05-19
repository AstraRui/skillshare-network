"""Fix messages check constraint to allow chat_id

Revision ID: 20260519_fix_msg_constraint
Revises: 20260519_fix_messages
Create Date: 2026-05-19 00:02:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_fix_msg_constraint"
down_revision: Union[str, None] = "20260519_fix_messages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_message_task_xor_exchange", "messages")
    op.create_check_constraint(
        "ck_message_context",
        "messages",
        "(chat_id IS NOT NULL AND task_id IS NULL) OR "
        "(task_id IS NOT NULL AND chat_id IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_message_context", "messages")
    op.create_check_constraint(
        "ck_message_task_xor_exchange",
        "messages",
        "(task_id IS NOT NULL AND exchange_id IS NULL) OR "
        "(task_id IS NULL AND exchange_id IS NOT NULL)",
    )
