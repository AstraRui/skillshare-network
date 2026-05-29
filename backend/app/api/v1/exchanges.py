from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.chat import create_chat, get_chat_by_exchange
from app.models.exchange import Exchange, ExchangeStatus
from app.ws.manager import manager
from app.models.listing import Listing, ListingInterest, ListingInterestStatus
from app.models.message import Message
from app.models.review import Review
from app.models.user import User
from app.policies.exchange_messaging import can_post_in_deal_chat
from app.schemas.exchange import (
    AcceptInterestRequest,
    ExchangeOut,
    ExchangeStatusUpdate,
    MessageCreate,
    MessageOut,
    ReviewCreate,
    ReviewOut,
)

router = APIRouter(prefix="/exchanges", tags=["exchanges"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def _get_exchange_participant_ids(db: AsyncSession, exchange: Exchange) -> set[int]:
    participants: set[int] = {exchange.initiator_id}
    if exchange.listing_id is None:
        return participants

    accepted_responder_id = await db.scalar(
        select(ListingInterest.responder_id).where(
            ListingInterest.listing_id == exchange.listing_id,
            ListingInterest.status == ListingInterestStatus.accepted,
        )
    )
    if accepted_responder_id is not None:
        participants.add(accepted_responder_id)
    return participants


async def _get_partner_user_id(db: AsyncSession, exchange: Exchange) -> int | None:
    if exchange.listing_id is None:
        return None
    return await db.scalar(
        select(ListingInterest.responder_id).where(
            ListingInterest.listing_id == exchange.listing_id,
            ListingInterest.status == ListingInterestStatus.accepted,
        )
    )


async def _require_exchange_member(db: AsyncSession, exchange: Exchange, user_id: int) -> None:
    participants = await _get_exchange_participant_ids(db, exchange)
    if user_id not in participants:
        raise HTTPException(status_code=403, detail="Only exchange members have access")


@router.post("/listing/{listing_id}/accept-interest", response_model=ExchangeOut)
async def accept_listing_interest(
    listing_id: int,
    payload: AcceptInterestRequest,
    db: DbSession,
    current_user: CurrentUser,
) -> Exchange:
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only listing author can accept interests")

    interest = await db.scalar(
        select(ListingInterest).where(
            ListingInterest.listing_id == listing_id,
            ListingInterest.responder_id == payload.responder_id,
        )
    )
    if interest is None:
        raise HTTPException(status_code=404, detail="Interest not found")

    existing = await db.scalar(
        select(Exchange).where(
            Exchange.listing_id == listing_id,
            Exchange.status.in_([ExchangeStatus.discussion, ExchangeStatus.active]),
        )
    )
    if existing is not None:
        raise HTTPException(status_code=409, detail="Active exchange already exists for listing")

    all_interests = list(
        await db.scalars(select(ListingInterest).where(ListingInterest.listing_id == listing_id))
    )
    for item in all_interests:
        item.status = (
            ListingInterestStatus.accepted
            if item.responder_id == payload.responder_id
            else ListingInterestStatus.rejected
        )

    exchange = Exchange(
        initiator_id=current_user.id,
        listing_id=listing_id,
        status=ExchangeStatus.discussion,
        is_chain=False,
    )
    db.add(exchange)
    await db.flush()
    await db.refresh(exchange)
    await create_chat(db, exchange.id)
    return exchange


@router.get("", response_model=list[ExchangeOut])
async def get_my_exchanges(db: DbSession, current_user: CurrentUser) -> list[Exchange]:
    stmt: Select[tuple[Exchange]] = (
        select(Exchange)
        .outerjoin(
            ListingInterest,
            and_(
                ListingInterest.listing_id == Exchange.listing_id,
                ListingInterest.status == ListingInterestStatus.accepted,
            ),
        )
        .where(
            or_(
                Exchange.initiator_id == current_user.id,
                ListingInterest.responder_id == current_user.id,
            )
        )
        .order_by(Exchange.created_at.desc())
    )
    return list(await db.scalars(stmt))


@router.post("/{exchange_id}/status", response_model=ExchangeOut)
async def update_exchange_status(
    exchange_id: int,
    payload: ExchangeStatusUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> Exchange:
    exchange = await db.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    await _require_exchange_member(db, exchange, current_user.id)

    allowed = {
        ExchangeStatus.discussion: {ExchangeStatus.active, ExchangeStatus.cancelled},
        ExchangeStatus.active: {ExchangeStatus.cancelled},
        ExchangeStatus.completed: set(),
        ExchangeStatus.cancelled: set(),
    }
    if payload.to not in allowed[exchange.status]:
        raise HTTPException(status_code=400, detail="Invalid status transition")

    exchange.status = payload.to
    if payload.to != ExchangeStatus.completed:
        exchange.completed_by_initiator = False
        exchange.completed_by_partner = False
        exchange.completed_at = None
        current_user.last_active_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(exchange)
    return exchange


@router.post("/{exchange_id}/confirm-completion", response_model=ExchangeOut)
async def confirm_exchange_completion(
    exchange_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> Exchange:
    exchange = await db.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    await _require_exchange_member(db, exchange, current_user.id)

    if exchange.status != ExchangeStatus.active:
        raise HTTPException(status_code=400, detail="Only active exchanges can be completed")

    partner_id = await _get_partner_user_id(db, exchange)
    if partner_id is None:
        raise HTTPException(status_code=400, detail="Cannot resolve second exchange member")

    if current_user.id == exchange.initiator_id:
        exchange.completed_by_initiator = True
    elif current_user.id == partner_id:
        exchange.completed_by_partner = True
    else:
        raise HTTPException(status_code=403, detail="Only exchange members can confirm completion")

    if exchange.completed_by_initiator and exchange.completed_by_partner:
        exchange.status = ExchangeStatus.completed
        exchange.completed_at = datetime.now(UTC)
        current_user.last_active_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(exchange)
    return exchange


@router.get("/{exchange_id}/messages", response_model=list[MessageOut])
async def get_exchange_messages(
    exchange_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[Message]:
    exchange = await db.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    await _require_exchange_member(db, exchange, current_user.id)

    chat = await get_chat_by_exchange(db, exchange_id)
    if chat is None:
        return []

    return list(
        await db.scalars(
            select(Message)
            .where(Message.chat_id == chat.id, Message.is_deleted.is_(False))
            .order_by(Message.created_at.asc())
        )
    )


@router.post(
    "/{exchange_id}/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED
)
async def post_exchange_message(
    exchange_id: int,
    payload: MessageCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Message:
    exchange = await db.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    await _require_exchange_member(db, exchange, current_user.id)

    if not can_post_in_deal_chat(exchange):
        raise HTTPException(status_code=400, detail="Exchange chat is read-only for current status")

    chat = await get_chat_by_exchange(db, exchange_id)
    if chat is None:
        chat = await create_chat(db, exchange_id)

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=400, detail="Message content cannot be empty")

    message = Message(
        chat_id=chat.id,
        sender_id=current_user.id,
        content=content,
    )
    db.add(message)
    current_user.last_active_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(message)

    # WebSocket broadcast для real-time доставки
    await manager.broadcast(
        chat.id,
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "sender_id": message.sender_id,
            "content": message.content,
            "media_url": message.media_url,
            "created_at": message.created_at.isoformat(),
            "edited_at": message.edited_at.isoformat() if message.edited_at else None,
            "is_deleted": message.is_deleted,
        },
    )

    return message


@router.post(
    "/{exchange_id}/reviews", response_model=ReviewOut, status_code=status.HTTP_201_CREATED
)
async def create_exchange_review(
    exchange_id: int,
    payload: ReviewCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> Review:
    exchange = await db.get(Exchange, exchange_id)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange not found")
    await _require_exchange_member(db, exchange, current_user.id)

    if exchange.status != ExchangeStatus.completed:
        raise HTTPException(
            status_code=400, detail="Reviews are available only for completed exchanges"
        )
    if payload.rating < 1 or payload.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be in range 1..5")

    partner_id = await _get_partner_user_id(db, exchange)
    if partner_id is None:
        raise HTTPException(status_code=400, detail="Cannot resolve review target")

    if current_user.id == exchange.initiator_id:
        reviewed_id = partner_id
    elif current_user.id == partner_id:
        reviewed_id = exchange.initiator_id
    else:
        raise HTTPException(status_code=403, detail="Only exchange members can review")

    review = Review(
        exchange_id=exchange.id,
        reviewer_id=current_user.id,
        reviewed_id=reviewed_id,
        rating=payload.rating,
        comment=payload.comment.strip() if payload.comment else None,
    )
    db.add(review)
    try:
        await db.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="You have already submitted a review") from exc

    avg_rating = await db.scalar(
        select(func.avg(Review.rating)).where(
            Review.reviewed_id == reviewed_id,
            Review.is_deleted.is_(False),
            Review.is_hidden.is_(False),
        )
    )
    reviewed_user = await db.get(User, reviewed_id)
    if reviewed_user is not None and avg_rating is not None:
        reviewed_user.rating = float(avg_rating)
        await db.flush()

    await db.refresh(review)
    return review
