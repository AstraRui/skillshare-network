import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Enum, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(20))
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=0)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role_enum"), nullable=False, default=UserRole.user)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    offered_skills = relationship("UserSkillsOffered", back_populates="user", cascade="all, delete-orphan")
    wanted_skills = relationship("UserSkillsWanted", back_populates="user", cascade="all, delete-orphan")
    initiated_exchanges = relationship("Exchange", foreign_keys="Exchange.initiator_id", back_populates="initiator")
    exchange_participants = relationship("ExchangeParticipant", back_populates="user", cascade="all, delete-orphan")
    assigned_tasks = relationship("Task", back_populates="assignee")
    messages = relationship("Message", back_populates="sender")
