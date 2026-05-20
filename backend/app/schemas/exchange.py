from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.exchange import ExchangeStatus


class AcceptInterestRequest(BaseModel):
    responder_id: int


class ExchangeOut(BaseModel):
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
    reviewed_id: int
    rating: int
    comment: str | None
