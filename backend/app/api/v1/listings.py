from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import Select, select
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


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    title: str
    description: str | None
    offering_summary: str
    seeking_summary: str
    status: ListingStatus
    created_at: datetime


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


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("", response_model=ListingOut, status_code=status.HTTP_201_CREATED)
async def create_listing(payload: ListingCreate, db: DbSession, current_user: CurrentUser) -> Listing:
    listing = Listing(
        author_id=current_user.id,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        offering_summary=payload.offering_summary.strip(),
        seeking_summary=payload.seeking_summary.strip(),
        status=payload.status,
    )
    db.add(listing)
    await db.flush()
    await db.refresh(listing)
    return listing


@router.get("", response_model=list[ListingOut])
async def get_listings(
    db: DbSession,
    status_filter: Annotated[ListingStatus | None, Query(alias="status")] = ListingStatus.published,
    author_id: int | None = None,
) -> list[Listing]:
    stmt: Select[tuple[Listing]] = select(Listing)
    if status_filter is not None:
        stmt = stmt.where(Listing.status == status_filter)
    if author_id is not None:
        stmt = stmt.where(Listing.author_id == author_id)
    stmt = stmt.order_by(Listing.created_at.desc())
    return list(await db.scalars(stmt))


@router.post("/{listing_id}/interests", response_model=ListingInterestOut, status_code=status.HTTP_201_CREATED)
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
    try:
        await db.flush()
    except IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Interest already exists") from exc

    await db.refresh(interest)
    return interest
