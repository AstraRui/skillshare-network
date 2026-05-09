"""Message endpoints."""

from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.message import Message
from app.schemas.chat import MessageCreate, MessageRead, MessageUpdate

from .connection_manager import manager
from .utils import _ensure_participant, _get_chat_or_404

router = APIRouter(prefix="/chat", tags=["chat"])
DB = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/chats/{chat_id}/messages", response_model=list[MessageRead])
async def get_chat_messages(
    chat_id: int,
    db: DB,
    user_id: int = Query(...),
) -> list[MessageRead]:
    await _get_chat_or_404(db, chat_id)
    await _ensure_participant(db, chat_id, user_id)

    result = await db.execute(
        select(Message)
        .where(Message.chat_id == chat_id, Message.is_deleted.is_(False))
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()


@router.post("/chats/{chat_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: int,
    payload: MessageCreate,
    db: DB,
) -> MessageRead:
    await _get_chat_or_404(db, chat_id)
    await _ensure_participant(db, chat_id, payload.sender_id)

    message = Message(
        chat_id=chat_id,
        sender_id=payload.sender_id,
        content=payload.content,
        media_url=payload.media_url,
        media_type=payload.media_type,
        media_size=payload.media_size,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    await manager.broadcast(
        chat_id,
        {
            "event": "message_created",
            "message": MessageRead.model_validate(message).model_dump(mode="json"),
        },
    )

    return message


@router.patch("/messages/{message_id}", response_model=MessageRead)
async def update_message(
    message_id: int,
    payload: MessageUpdate,
    db: DB,
    user_id: int = Query(...),
) -> MessageRead:
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.is_deleted.is_(False))
    )
    message = result.scalars().first()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if message.sender_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sender can edit message")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)

    message.edited_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(message)

    if message.chat_id is not None:
        await manager.broadcast(
            message.chat_id,
            {
                "event": "message_updated",
                "message": MessageRead.model_validate(message).model_dump(mode="json"),
            },
        )

    return message


@router.delete("/messages/{message_id}", status_code=status.HTTP_200_OK)
async def delete_message(
    message_id: int,
    db: DB,
    user_id: int = Query(...),
) -> dict[str, Any]:
    result = await db.execute(
        select(Message).where(Message.id == message_id, Message.is_deleted.is_(False))
    )
    message = result.scalars().first()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    if message.sender_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sender can delete message")

    message.is_deleted = True
    await db.commit()

    if message.chat_id is not None:
        await manager.broadcast(chat_id=message.chat_id, payload={"event": "message_deleted", "message_id": message.id})

    return {"status": "deleted", "message_id": message.id}