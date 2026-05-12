"""ТЗ: объявления, отклики, связь сделки с объявлением, статусы сделки, чат на уровне exchange.

Revision ID: a1b2c3d4e5f6
Revises: 44d97bedf816
Create Date: 2026-02-05

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "a1b2c3d4e5f6"
down_revision = "44d97bedf816"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    listing_status = postgresql.ENUM(
        "draft",
        "published",
        "archived",
        name="listing_status_enum",
    )
    listing_status.create(bind, checkfirst=True)

    interest_status = postgresql.ENUM(
        "pending",
        "withdrawn",
        "accepted",
        "rejected",
        name="listing_interest_status_enum",
    )
    interest_status.create(bind, checkfirst=True)

    op.create_table(
        "listings",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("offering_summary", sa.Text(), nullable=False),
        sa.Column("seeking_summary", sa.Text(), nullable=False),
        sa.Column(
            "status",
            postgresql.ENUM(
                "draft",
                "published",
                "archived",
                name="listing_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listings_author_id"), "listings", ["author_id"], unique=False)
    op.create_index(op.f("ix_listings_status"), "listings", ["status"], unique=False)

    op.create_table(
        "listing_interests",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("listing_id", sa.BigInteger(), nullable=False),
        sa.Column("responder_id", sa.BigInteger(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "status",
            postgresql.ENUM(
                "pending",
                "withdrawn",
                "accepted",
                "rejected",
                name="listing_interest_status_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["responder_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("listing_id", "responder_id", name="uq_listing_interest_responder"),
    )
    op.create_index(
        op.f("ix_listing_interests_listing_id"), "listing_interests", ["listing_id"], unique=False
    )
    op.create_index(
        op.f("ix_listing_interests_responder_id"),
        "listing_interests",
        ["responder_id"],
        unique=False,
    )

    op.add_column("exchanges", sa.Column("listing_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        "fk_exchanges_listing_id_listings",
        "exchanges",
        "listings",
        ["listing_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_exchanges_listing_id"), "exchanges", ["listing_id"], unique=False)

    op.execute(
        sa.text(
            "UPDATE exchanges SET status = 'discussion' "
            "WHERE status IS NULL OR status NOT IN "
            "('discussion', 'active', 'completed', 'cancelled')"
        )
    )

    op.add_column("messages", sa.Column("exchange_id", sa.BigInteger(), nullable=True))
    op.alter_column("messages", "task_id", existing_type=sa.BigInteger(), nullable=True)
    op.create_foreign_key(
        "fk_messages_exchange_id_exchanges",
        "messages",
        "exchanges",
        ["exchange_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(op.f("ix_messages_exchange_id"), "messages", ["exchange_id"], unique=False)
    op.create_check_constraint(
        "ck_message_task_xor_exchange",
        "messages",
        "(task_id IS NOT NULL AND exchange_id IS NULL) OR "
        "(task_id IS NULL AND exchange_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM messages WHERE exchange_id IS NOT NULL"))

    op.drop_constraint("ck_message_task_xor_exchange", "messages", type_="check")
    op.drop_index(op.f("ix_messages_exchange_id"), table_name="messages")
    op.drop_constraint("fk_messages_exchange_id_exchanges", "messages", type_="foreignkey")
    op.drop_column("messages", "exchange_id")

    op.alter_column(
        "messages",
        "task_id",
        existing_type=sa.BigInteger(),
        nullable=False,
    )

    op.drop_index(op.f("ix_exchanges_listing_id"), table_name="exchanges")
    op.drop_constraint("fk_exchanges_listing_id_listings", "exchanges", type_="foreignkey")
    op.drop_column("exchanges", "listing_id")

    op.drop_table("listing_interests")
    op.drop_table("listings")

    op.execute(sa.text("DROP TYPE IF EXISTS listing_interest_status_enum CASCADE"))
    op.execute(sa.text("DROP TYPE IF EXISTS listing_status_enum CASCADE"))
