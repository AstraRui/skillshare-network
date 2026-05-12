from datetime import datetime

from pydantic import BaseModel

from app.models import ChatStatus
from app.schemas.message import MessageRead


class ChatRead(BaseModel):
    model_config = {"from attributes": True}

    id: int
    exchange_id: int
    status: ChatStatus
    created_at: datetime
    messages: list[MessageRead] = []