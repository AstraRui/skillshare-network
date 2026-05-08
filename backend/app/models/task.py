from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    exchange_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("exchanges.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assignee_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="todo")

    exchange = relationship("Exchange", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")