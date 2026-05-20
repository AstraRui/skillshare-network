from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.listing import Listing, ListingInterest, ListingInterestStatus, ListingStatus
from app.models.user import User

router = APIRouter(prefix="/listings", tags=["listings"])


class ListingCreate(BaseModel):
    title: str
    description: str | None = None
    offering_summary: str
    seeking_summary: str
    status: ListingStatus = ListingStatus.published


class ListingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    offering_summary: str | None = None
    seeking_summary: str | None = None
    status: ListingStatus | None = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    author_full_name: str | None = None
    title: str
    description: str | None
    offering_summary: str
    seeking_summary: str
    status: ListingStatus
    created_at: datetime


def listing_to_out(listing: Listing, author_full_name: str | None = None) -> ListingOut:
    return ListingOut(
        id=listing.id,
        author_id=listing.author_id,
        author_full_name=author_full_name,
        title=listing.title,
        description=listing.description,
        offering_summary=listing.offering_summary,
        seeking_summary=listing.seeking_summary,
        status=listing.status,
        created_at=listing.created_at,
    )


class ListingInterestCreate(BaseModel):
    message: str | None = None


class ListingInterestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    responder_id: int
    message: str | None
    status: ListingInterestStatus
    created_at: datetime


class ListingInterestDetailOut(ListingInterestOut):
    listing_title: str
    responder_full_name: str | None = None


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: ListingCreate, db: DbSession, current_user: CurrentUser
) -> ListingOut:
    listing = Listing(
        author_id=current_user.id,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        offering_summary=payload.offering_summary.strip(),
        seeking_summary=payload.seeking_summary.strip(),
        status=payload.status,
    )
    db.add(listing)
    current_user.last_active_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(listing)
    return listing_to_out(listing, current_user.full_name)


@router.get("/me/incoming-interests", response_model=list[ListingInterestDetailOut])
async def get_my_incoming_interests(
    db: DbSession, current_user: CurrentUser
) -> list[ListingInterestDetailOut]:
    rows = await db.execute(
        select(ListingInterest, Listing.title, User.full_name)
        .join(Listing, Listing.id == ListingInterest.listing_id)
        .join(User, User.id == ListingInterest.responder_id)
        .where(
            Listing.author_id == current_user.id,
            ListingInterest.status == ListingInterestStatus.pending,
        )
        .order_by(ListingInterest.created_at.desc())
    )
    return [
        ListingInterestDetailOut(
            id=interest.id,
            listing_id=interest.listing_id,
            responder_id=interest.responder_id,
            message=interest.message,
            status=interest.status,
            created_at=interest.created_at,
            listing_title=title,
            responder_full_name=full_name,
        )
        for interest, title, full_name in rows.all()
    ]


@router.patch("/{listing_id}", response_model=ListingOut)
async def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ListingOut:
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только автор может редактировать объявление")

    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=400, detail="Заголовок не может быть пустым")
        listing.title = title
    if payload.description is not None:
        listing.description = payload.description.strip() or None
    if payload.offering_summary is not None:
        offering = payload.offering_summary.strip()
        if not offering:
            raise HTTPException(status_code=400, detail="Поле «предлагаю» не может быть пустым")
        listing.offering_summary = offering
    if payload.seeking_summary is not None:
        seeking = payload.seeking_summary.strip()
        if not seeking:
            raise HTTPException(status_code=400, detail="Поле «ищу» не может быть пустым")
        listing.seeking_summary = seeking
    if payload.status is not None:
        listing.status = payload.status

    current_user.last_active_at = datetime.now(UTC)
    await db.flush()
    await db.refresh(listing)
    return listing_to_out(listing, current_user.full_name)


@router.get("/{listing_id}/interests", response_model=list[ListingInterestDetailOut])
async def get_listing_interests(
    listing_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> list[ListingInterestDetailOut]:
    listing = await db.get(Listing, listing_id)
    if listing is None:
        raise HTTPException(status_code=404, detail="Объявление не найдено")
    if listing.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Только автор объявления видит отклики")

    rows = await db.execute(
        select(ListingInterest, Listing.title, User.full_name)
        .join(Listing, Listing.id == ListingInterest.listing_id)
        .join(User, User.id == ListingInterest.responder_id)
        .where(
            ListingInterest.listing_id == listing_id,
            ListingInterest.status == ListingInterestStatus.pending,
        )
        .order_by(ListingInterest.created_at.desc())
    )
    return [
        ListingInterestDetailOut(
            id=interest.id,
            listing_id=interest.listing_id,
            responder_id=interest.responder_id,
            message=interest.message,
            status=interest.status,
            created_at=interest.created_at,
            listing_title=title,
            responder_full_name=full_name,
        )
        for interest, title, full_name in rows.all()
    ]


@router.get("", response_model=list[ListingOut])
async def get_listings(
    db: DbSession,
    status_filter: Annotated[ListingStatus | None, Query(alias="status")] = ListingStatus.published,
    author_id: int | None = None,
) -> list[ListingOut]:
    stmt = (
        select(Listing, User.full_name)
        .join(User, User.id == Listing.author_id)
        .where(User.is_deleted.is_(False))
    )
    if status_filter is not None:
        stmt = stmt.where(Listing.status == status_filter)
    if author_id is not None:
        stmt = stmt.where(Listing.author_id == author_id)
    stmt = stmt.order_by(Listing.created_at.desc())
    rows = await db.execute(stmt)
    return [listing_to_out(listing, full_name) for listing, full_name in rows.all()]


@router.post(
    "/{listing_id}/interests",
    response_model=ListingInterestOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_listing_interest(
    listing_id: int,
    payload: ListingInterestCreate,
    db: DbSession,
    current_user: CurrentUser,
) -> ListingInterest:
    listing = await db.get(Listing, listing_id)
    if listing is None or listing.status != ListingStatus.published:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.author_id == current_user.id:
        raise HTTPException(status_code=400, detail="Author cannot respond to own listing")

    interest = ListingInterest(
        listing_id=listing_id,
        responder_id=current_user.id,
        message=payload.message.strip() if payload.message else None,
        status=ListingInterestStatus.pending,
    )
    db.add(interest)
    current_user.last_active_at = datetime.now(UTC)
    try:
        await db.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Interest already exists") from exc

    await db.refresh(interest)
    return interest
