"""Бизнес-логика для операций с пользователями."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exchange import Exchange, ExchangeStatus
from app.models.listing import ListingInterest, ListingInterestStatus


async def cancel_user_exchanges(db: AsyncSession, user_id: int) -> None:
    """Отменяет все активные сделки пользователя (как initiator или responder)."""
    # Отменяем сделки где пользователь initiator
    initiator_exchanges = list(
        await db.scalars(
            select(Exchange).where(
                Exchange.initiator_id == user_id,
                Exchange.status.in_([ExchangeStatus.discussion, ExchangeStatus.active]),
                Exchange.is_deleted.is_(False),
            )
        )
    )
    for exchange in initiator_exchanges:
        exchange.status = ExchangeStatus.cancelled

    # Отменяем сделки где пользователь responder (через ListingInterest)
    responder_interests = list(
        await db.scalars(
            select(ListingInterest).where(
                ListingInterest.responder_id == user_id,
                ListingInterest.status == ListingInterestStatus.accepted,
            )
        )
    )
    listing_ids = [interest.listing_id for interest in responder_interests]
    if listing_ids:
        responder_exchanges = list(
            await db.scalars(
                select(Exchange).where(
                    Exchange.listing_id.in_(listing_ids),
                    Exchange.status.in_([ExchangeStatus.discussion, ExchangeStatus.active]),
                    Exchange.is_deleted.is_(False),
                )
            )
        )
        for exchange in responder_exchanges:
            exchange.status = ExchangeStatus.cancelled
