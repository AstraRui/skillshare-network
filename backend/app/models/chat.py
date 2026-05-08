from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


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
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    exchange = relationship("Exchange", back_populates="chat", uselist=False)
    participants = relationship(
        "ChatParticipant", back_populates="chat", cascade="all, delete-orphan"
    )
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    chat_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), primary_key=True
    )

    chat = relationship("Chat", back_populates="participants")
    user = relationship("User", back_populates="chat_participants")
