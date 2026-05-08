from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session, selectinload

from app.db.session import SessionLocal, get_db
from app.models.chat import Chat, ChatParticipant
from app.models.message import Message
from app.schemas.chat import ChatCreate, ChatRead, MessageCreate, MessageRead, MessageUpdate

router = APIRouter(tags=["chats"])

DbSession = Annotated[Session, Depends(get_db)]


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

    async def broadcast(self, chat_id: int, payload: dict[str, Any]) -> None:
        connections = list(self.active_connections.get(chat_id, []))
        for connection in connections:
            await connection.send_json(payload)


manager = ChatConnectionManager()


def _chat_to_read(chat: Chat) -> ChatRead:
    return ChatRead(
        id=chat.id,
        title=chat.title,
        is_group=chat.is_group,
        created_by_id=chat.created_by_id,
        participant_ids=[participant.user_id for participant in chat.participants],
        created_at=chat.created_at,
    )


def _get_chat_or_404(db: Session, chat_id: int) -> Chat:
    chat = (
        db.query(Chat)
        .options(selectinload(Chat.participants))
        .filter(Chat.id == chat_id, Chat.is_deleted.is_(False))
        .first()
    )
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


def _ensure_participant(db: Session, chat_id: int, user_id: int) -> None:
    participant = (
        db.query(ChatParticipant)
        .filter(ChatParticipant.chat_id == chat_id, ChatParticipant.user_id == user_id)
        .first()
    )
    if participant is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not a chat participant",
        )


@router.get("/chats", response_model=list[ChatRead])
def get_chats(
    db: DbSession,
    user_id: int | None = Query(default=None),
) -> list[ChatRead]:
    query = (
        db.query(Chat)
        .options(selectinload(Chat.participants))
        .filter(Chat.is_deleted.is_(False))
        .order_by(Chat.created_at.desc())
    )

    if user_id is not None:
        query = query.join(ChatParticipant).filter(ChatParticipant.user_id == user_id)

    return [_chat_to_read(chat) for chat in query.all()]


@router.get("/chats/{chat_id}", response_model=ChatRead)
def get_chat(chat_id: int, db: DbSession) -> ChatRead:
    return _chat_to_read(_get_chat_or_404(db, chat_id))


@router.post("/chats", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
def create_chat(payload: ChatCreate, db: DbSession) -> ChatRead:
    participant_ids = set(payload.participant_ids)
    participant_ids.add(payload.created_by_id)

    chat = Chat(
        title=payload.title,
        created_by_id=payload.created_by_id,
        is_group=len(participant_ids) > 2,
    )
    db.add(chat)
    db.flush()

    for user_id in participant_ids:
        db.add(ChatParticipant(chat_id=chat.id, user_id=user_id))

    db.commit()
    db.refresh(chat)

    chat = (
        db.query(Chat)
        .options(selectinload(Chat.participants))
        .filter(Chat.id == chat.id)
        .one()
    )
    return _chat_to_read(chat)


@router.delete("/chats/{chat_id}", status_code=status.HTTP_200_OK)
def delete_chat(
    chat_id: int,
    db: DbSession,
    user_id: int | None = Query(default=None),
) -> dict[str, str]:
    chat = _get_chat_or_404(db, chat_id)

    if user_id is not None:
        _ensure_participant(db, chat_id, user_id)

    chat.is_deleted = True
    chat.deleted_at = datetime.now(UTC)
    db.commit()

    return {"status": "deleted"}


@router.get("/chats/{chat_id}/messages", response_model=list[MessageRead])
def get_chat_messages(
    chat_id: int,
    db: DbSession,
    user_id: int | None = Query(default=None),
) -> list[MessageRead]:
    _get_chat_or_404(db, chat_id)

    if user_id is not None:
        _ensure_participant(db, chat_id, user_id)

    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id, Message.is_deleted.is_(False))
        .order_by(Message.created_at.asc())
        .all()
    )


@router.post("/chats/{chat_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: int,
    payload: MessageCreate,
    db: DbSession,
) -> MessageRead:
    _get_chat_or_404(db, chat_id)
    _ensure_participant(db, chat_id, payload.sender_id)

    message = Message(
        chat_id=chat_id,
        sender_id=payload.sender_id,
        content=payload.content,
        media_url=payload.media_url,
        media_type=payload.media_type,
        media_size=payload.media_size,
    )
    db.add(message)
    db.commit()
    db.refresh(message)

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
    db: DbSession,
    user_id: int | None = Query(default=None),
) -> MessageRead:
    message = db.query(Message).filter(Message.id == message_id, Message.is_deleted.is_(False)).first()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    if user_id is not None and message.sender_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sender can edit message")

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(message, field, value)

    now = datetime.now(UTC)
    message.edited_at = now
    message.updated_at = now
    db.commit()
    db.refresh(message)

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
    db: DbSession,
    user_id: int | None = Query(default=None),
) -> dict[str, str | int]:
    message = db.query(Message).filter(Message.id == message_id, Message.is_deleted.is_(False)).first()

    if message is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    if user_id is not None and message.sender_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sender can delete message")

    message.is_deleted = True
    message.updated_at = datetime.now(UTC)
    db.commit()

    if message.chat_id is not None:
        await manager.broadcast(message.chat_id, {"event": "message_deleted", "message_id": message.id})

    return {"status": "deleted", "message_id": message.id}


@router.websocket("/chats/{chat_id}/ws")
async def websocket_chat(chat_id: int, websocket: WebSocket) -> None:
    await manager.connect(chat_id, websocket)
    db = SessionLocal()

    try:
        _get_chat_or_404(db, chat_id)

        while True:
            raw_data = await websocket.receive_text()

            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError:
                data = {"content": raw_data}

            sender_id = data.get("sender_id")
            content = data.get("content")
            media_url = data.get("media_url")
            media_type = data.get("media_type")
            media_size = data.get("media_size")

            if sender_id is None:
                await websocket.send_json({"event": "error", "detail": "sender_id is required"})
                continue

            _ensure_participant(db, chat_id, int(sender_id))

            message = Message(
                chat_id=chat_id,
                sender_id=int(sender_id),
                content=content,
                media_url=media_url,
                media_type=media_type,
                media_size=media_size,
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            await manager.broadcast(
                chat_id,
                {
                    "event": "message_created",
                    "message": MessageRead.model_validate(message).model_dump(mode="json"),
                },
            )
    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
    except HTTPException as exc:
        await websocket.send_json({"event": "error", "detail": exc.detail})
        manager.disconnect(chat_id, websocket)
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
    finally:
        db.close()
