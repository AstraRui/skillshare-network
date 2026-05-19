"""Add chats and fix messages table

Revision ID: 20260519_add_chats
Revises: 20260513_add_last_active_at
Create Date: 2026-05-19 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260519_add_chats"
down_revision: Union[str, None] = "20260513_add_last_active_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column(
            "exchange_id",
            sa.BigInteger(),
            sa.ForeignKey("exchanges.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "closed", name="chat_status_enum"),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chats_exchange_id", "chats", ["exchange_id"])

    # Добавляем chat_id в messages (nullable — для обратной совместимости)
    op.add_column(
        "messages",
        sa.Column(
            "chat_id",
            sa.BigInteger(),
            sa.ForeignKey("chats.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.create_index("ix_messages_chat_id", "messages", ["chat_id"])


def downgrade() -> None:
    op.drop_index("ix_messages_chat_id", "messages")
    op.drop_column("messages", "chat_id")
    op.drop_index("ix_chats_exchange_id", "chats")
    op.drop_table("chats")
    op.execute("DROP TYPE IF EXISTS chat_status_enum")
