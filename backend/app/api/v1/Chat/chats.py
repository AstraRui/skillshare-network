from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.chat import Chat, ChatParticipant
from app.models.exchange import Exchange
from app.schemas.chat import ChatCreate, ChatRead

from .connection_manager import manager
from .utils import _chat_to_read, _ensure_participant, _get_chat_or_404

router = APIRouter(prefix="/chat", tags=["chat"])
DB = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/chats", response_model=list[ChatRead])
async def get_chats(
    db: DB,
    user_id: int | None = Query(default=None),
) -> list[ChatRead]:
    query = select(Chat).options(selectinload(Chat.participants)).where(Chat.is_deleted.is_(False)).order_by(Chat.created_at.desc())

    if user_id is not None:
        query = query.join(ChatParticipant).where(ChatParticipant.user_id == user_id)

    result = await db.execute(query)
    chats = result.scalars().all()
    return [_chat_to_read(chat) for chat in chats]


@router.get("/chats/{chat_id}", response_model=ChatRead)
async def get_chat(chat_id: int, db: DB) -> ChatRead:
    return _chat_to_read(await _get_chat_or_404(db, chat_id))


@router.post("/chats", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(payload: ChatCreate, db: DB) -> ChatRead:
    result = await db.execute(
        select(Exchange).options(selectinload(Exchange.participants)).where(
            Exchange.id == payload.exchange_id,
            Exchange.is_deleted.is_(False),
        )
    )
    exchange = result.scalars().first()
    if exchange is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exchange not found")

    existing_chat = await db.execute(select(Chat).where(Chat.exchange_id == payload.exchange_id))
    if existing_chat.scalars().first() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Chat already exists for this exchange",
        )

    chat = Chat(exchange_id=payload.exchange_id, status="active")
    db.add(chat)
    await db.flush()

    for participant in exchange.participants:
        db.add(ChatParticipant(chat_id=chat.id, user_id=participant.user_id))

    await db.commit()
    await db.refresh(chat)

    return _chat_to_read(chat)


@router.delete("/chats/{chat_id}", status_code=status.HTTP_200_OK)
async def delete_chat(
    chat_id: int,
    db: DB,
    user_id: int = Query(...),
) -> dict[str, str]:
    chat = await _get_chat_or_404(db, chat_id)
    await _ensure_participant(db, chat_id, user_id)

    chat.is_deleted = True
    chat.deleted_at = datetime.now(UTC)
    await db.commit()

    return {"status": "deleted"}