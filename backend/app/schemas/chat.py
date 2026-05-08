from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatCreate(BaseModel):
    exchange_id: int


class ChatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_id: int
    participant_ids: list[int]
    status: str
    created_at: datetime


class MessageCreate(BaseModel):
    sender_id: int
    content: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    media_size: int | None = None


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    chat_id: int
    sender_id: int
    content: str | None
    media_url: str | None
    media_type: str | None
    media_size: int | None
    created_at: datetime
    is_deleted: bool
    edited_at: datetime | None


class MessageUpdate(BaseModel):
    content: str | None = None
    media_url: str | None = None
    media_type: str | None = None
    media_size: int | None = None
