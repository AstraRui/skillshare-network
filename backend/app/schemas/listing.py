from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.listing import ListingInterestStatus, ListingStatus


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
    responder_full_name: str


def listing_to_out(listing: object, author_full_name: str | None) -> ListingOut:
    data = ListingOut.model_validate(listing)
    return data.model_copy(update={"author_full_name": author_full_name})
