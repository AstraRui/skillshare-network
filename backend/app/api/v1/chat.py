"""Chat API for exchange-based conversations."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db_session
from app.models.chat import Chat, ChatParticipant
from app.models.exchange import Exchange
from app.models.message import Message
from app.schemas.chat import ChatCreate, ChatRead, MessageCreate, MessageRead, MessageUpdate

router = APIRouter(prefix="/chat", tags=["chat"])
DB = Annotated[AsyncSession, Depends(get_db_session)]


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(chat_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and chat_id in self.active_connections:
            del self.active_connections[chat_id]

    async def broadcast(self, chat_id: int, payload: dict[str, object]) -> None:
        connections = list(self.active_connections.get(chat_id, []))
        for connection in connections:
            await connection.send_json(payload)


manager = ChatConnectionManager()


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
) -> dict[str, object]:
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


@router.websocket("/ws")
async def websocket_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            msg = await websocket.receive_text()
            await websocket.send_text(f"echo: {msg}")
    except WebSocketDisconnect:
        return
