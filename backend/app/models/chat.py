import enum
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ChatStatus(enum.StrEnum):
    active = "active"
    closed = "closed"


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exchanges.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    status: Mapped[ChatStatus] = mapped_column(
        Enum(ChatStatus, name="chat_status_enum"), nullable=False, default=ChatStatus.active
    )

    exchange = relationship("Exchange", back_populates="chat")
