"""Объявления (предложения об обмене) и отклики — слой под ТЗ «публикация → отклик → сделка»."""

from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ListingStatus(enum.StrEnum):
    draft = "draft"
    published = "published"
    archived = "archived"


class ListingInterestStatus(enum.StrEnum):
    pending = "pending"
    withdrawn = "withdrawn"
    accepted = "accepted"
    rejected = "rejected"


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    author_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    offering_summary: Mapped[str] = mapped_column(Text, nullable=False)
    seeking_summary: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ListingStatus] = mapped_column(
        Enum(ListingStatus, name="listing_status_enum"),
        nullable=False,
        default=ListingStatus.draft,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    author = relationship("User", back_populates="listings")
    interests = relationship(
        "ListingInterest", back_populates="listing", cascade="all, delete-orphan"
    )
    exchanges = relationship("Exchange", back_populates="listing")


class ListingInterest(Base):
    """Отклик другого пользователя на объявление."""

    __tablename__ = "listing_interests"
    __table_args__ = (
        UniqueConstraint("listing_id", "responder_id", name="uq_listing_interest_responder"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False, index=True
    )
    responder_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    message: Mapped[str | None] = mapped_column(Text)
    status: Mapped[ListingInterestStatus] = mapped_column(
        Enum(ListingInterestStatus, name="listing_interest_status_enum"),
        nullable=False,
        default=ListingInterestStatus.pending,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    listing = relationship("Listing", back_populates="interests")
    responder = relationship("User", back_populates="listing_interests")
