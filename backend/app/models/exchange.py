import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExchangeStatus(enum.StrEnum):
    """Жизненный цикл сделки (ТЗ): обсуждение → активный обмен → завершение / отмена."""

    discussion = "discussion"
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class Exchange(Base):
    __tablename__ = "exchanges"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    initiator_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    listing_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("listings.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[ExchangeStatus] = mapped_column(
        Enum(ExchangeStatus, name="exchange_status_enum", native_enum=False, length=32),
        nullable=False,
        default=ExchangeStatus.discussion,
    )
    is_chain: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_by_initiator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    completed_by_partner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    # Двухстороннее подтверждение начала обмена
    started_by_initiator: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_by_partner: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_moderated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    moderated_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    listing = relationship("Listing", back_populates="exchanges")
    initiator = relationship(
        "User", foreign_keys=[initiator_id], back_populates="initiated_exchanges"
    )
    moderator = relationship("User", foreign_keys=[moderated_by])
    participants = relationship(
        "ExchangeParticipant", back_populates="exchange", cascade="all, delete-orphan"
    )
    tasks = relationship("Task", back_populates="exchange", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="exchange", cascade="all, delete-orphan")
    chat = relationship(
        "Chat", back_populates="exchange", uselist=False, cascade="all, delete-orphan"
    )


class ExchangeParticipant(Base):
    __tablename__ = "exchange_participants"
    __table_args__ = (UniqueConstraint("exchange_id", "user_id", name="uq_exchange_participant"),)

    exchange_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exchanges.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )
    gives_skill_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    gets_skill_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    position: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    exchange = relationship("Exchange", foreign_keys=[exchange_id], back_populates="participants")
    user = relationship("User", back_populates="exchange_participants")
    gives_skill = relationship("Skill", foreign_keys=[gives_skill_id])
    gets_skill = relationship("Skill", foreign_keys=[gets_skill_id])
