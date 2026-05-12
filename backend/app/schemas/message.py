from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str | None = None
    media_url: str | None = None

class MessageRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    chat_id: int
    sender_id: int
    content: str | None
    media_url: str | None
    created_at: datetime
    edited_at: datetime | None
    is_deleted: bool

class MessageUpdate(BaseModel):
    content: str