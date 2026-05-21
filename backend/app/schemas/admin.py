from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.chat import ChatStatus
from app.models.exchange import ExchangeStatus
from app.models.listing import ListingStatus
from app.models.user import UserRole


class AdminUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    phone: str | None
    full_name: str | None
    rating: float
    role: UserRole
    is_deleted: bool
    deleted_at: datetime | None
    created_at: datetime


class UserStatusPatch(BaseModel):
    is_deleted: bool | None = None
    role: UserRole | None = None


class AdminListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    title: str
    description: str | None
    offering_summary: str
    seeking_summary: str
    status: ListingStatus
    created_at: datetime


class ListingStatusPatch(BaseModel):
    status: ListingStatus


class AdminExchangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    initiator_id: int
    listing_id: int | None
    status: ExchangeStatus
    is_chain: bool
    created_at: datetime
    completed_at: datetime | None
    completed_by_initiator: bool
    completed_by_partner: bool
    is_deleted: bool
    deleted_at: datetime | None


class ExchangeStatusPatch(BaseModel):
    status: ExchangeStatus


class AdminChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_id: int
    status: ChatStatus
    created_at: datetime


class AdminMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    exchange_id: int | None
    task_id: int | None
    sender_id: int
    content: str | None
    media_url: str | None
    media_type: str | None
    media_size: int | None
    created_at: datetime
    edited_at: datetime | None
    is_deleted: bool


class AdminReportOut(BaseModel):
    id: int
    status: str
    message: str
