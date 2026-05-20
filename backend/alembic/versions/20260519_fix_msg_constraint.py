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
    # Старые сообщения сделок хранили exchange_id; привязываем к chats.chat_id
    op.execute(
        sa.text(
            """
            INSERT INTO chats (exchange_id, status, created_at)
            SELECT DISTINCT m.exchange_id, 'active'::chat_status_enum, NOW()
            FROM messages m
            WHERE m.exchange_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1 FROM chats c WHERE c.exchange_id = m.exchange_id
              )
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE messages m
            SET chat_id = c.id
            FROM chats c
            WHERE m.exchange_id = c.exchange_id
              AND m.chat_id IS NULL
              AND m.exchange_id IS NOT NULL
            """
        )
    )
    # Чаты для exchanges без сообщений, но уже созданных после accept-interest
    op.execute(
        sa.text(
            """
            INSERT INTO chats (exchange_id, status, created_at)
            SELECT e.id, 'active'::chat_status_enum, NOW()
            FROM exchanges e
            WHERE NOT EXISTS (SELECT 1 FROM chats c WHERE c.exchange_id = e.id)
            """
        )
    )

    op.execute(
        sa.text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS ck_message_task_xor_exchange")
    )
    op.execute(sa.text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS ck_message_context"))

    op.create_check_constraint(
        "ck_message_context",
        "messages",
        "(chat_id IS NOT NULL AND task_id IS NULL) OR "
        "(task_id IS NOT NULL AND chat_id IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_message_context", "messages", type_="check")
    op.create_check_constraint(
        "ck_message_task_xor_exchange",
        "messages",
        "(task_id IS NOT NULL AND exchange_id IS NULL) OR "
        "(task_id IS NULL AND exchange_id IS NOT NULL)",
    )
