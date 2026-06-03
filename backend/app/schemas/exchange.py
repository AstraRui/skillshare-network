from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.exchange import ExchangeStatus


class AcceptInterestRequest(BaseModel):
    responder_id: int


class DirectExchangeRequest(BaseModel):
    target_user_id: int


class ExchangeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    initiator_id: int
    partner_id: int | None = None
    partner_name: str | None = None
    listing_id: int | None = None
    listing_title: str | None = None
    status: ExchangeStatus
    is_chain: bool
    created_at: datetime
    completed_at: datetime | None
    completed_by_initiator: bool
    completed_by_partner: bool
    # Двухстороннее подтверждение начала
    started_by_initiator: bool
    started_by_partner: bool
    started_at: datetime | None


class ExchangeStatusUpdate(BaseModel):
    to: ExchangeStatus


class MessageCreate(BaseModel):
    content: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    task_id: int | None
    sender_id: int
    content: str | None
    created_at: datetime


class ReviewCreate(BaseModel):
    rating: int
    comment: str | None = None


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_id: int
    reviewer_id: int
    reviewer_name: str | None = None
    reviewed_id: int
    rating: int
    comment: str | None
