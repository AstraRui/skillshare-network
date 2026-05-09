"""Utility functions for chat API."""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.chat import Chat, ChatParticipant
from app.schemas.chat import ChatRead


def _chat_to_read(chat: Chat) -> ChatRead:
    return ChatRead(
        id=chat.id,
        exchange_id=chat.exchange_id,
        participant_ids=[participant.user_id for participant in chat.participants],
        status=chat.status,
        created_at=chat.created_at,
    )


async def _get_chat_or_404(db: AsyncSession, chat_id: int) -> Chat:
    result = await db.execute(
        select(Chat).options(selectinload(Chat.participants)).where(
            Chat.id == chat_id,
            Chat.is_deleted.is_(False),
        )
    )
    chat = result.scalars().first()
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


async def _ensure_participant(db: AsyncSession, chat_id: int, user_id: int) -> None:
    result = await db.execute(
        select(ChatParticipant).where(
            ChatParticipant.chat_id == chat_id,
            ChatParticipant.user_id == user_id,
        )
    )
    participant = result.scalars().first()
    if participant is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a chat participant",
        )