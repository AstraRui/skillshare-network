from __future__ import annotations

from typing import Annotated

import jwt
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.params import Depends
from jwt import PyJWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.settings import settings
from app.crud import chat as chat_crud
from app.crud import message as message_crud
from app.db.session import SessionLocal, get_db_session
from app.models import Message
from app.models.user import User
from app.schemas.chat import ChatRead
from app.schemas.message import MessageCreate, MessageRead, MessageUpdate
from app.ws.manager import manager

router = APIRouter(prefix="/chat", tags=["chat"])
DB = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/exchanges/{exchange_id}", response_model=ChatRead)
async def get_chat(exchange_id: int, db: DB):
    chat = await chat_crud.get_chat_by_exchange(db, exchange_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_messages(chat_id: int, db: DB):
    return await message_crud.get_messages(db, chat_id)


@router.post("/{chat_id}/messages", response_model=MessageRead, status_code=201)
async def send_message(chat_id: int, body: MessageCreate, db: DB, current_user: CurrentUser):
    chat = await chat_crud.get_chat_by_exchange(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    msg = await message_crud.create_message(
        db,
        chat_id=chat.id,
        sender_id=current_user.id,
        content=body.content,
        media_url=body.media_url,
    )
    # Рассылаем новое сообщение всем подключённым по WS
    await manager.broadcast(
        chat.id,
        {
            "id": msg.id,
            "chat_id": msg.chat_id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "media_url": msg.media_url,
            "created_at": msg.created_at.isoformat(),
            "edited_at": msg.edited_at.isoformat() if msg.edited_at else None,
            "is_deleted": msg.is_deleted,
        },
    )
    return msg


@router.websocket("/{chat_id}/ws")
async def chat_websocket(
    chat_id: int,
    websocket: WebSocket,
    token: str | None = None,
):
    """
    WebSocket-эндпоинт для real-time чата.
    Подключение: ws://host/api/v1/chat/{chat_id}/ws?token=<jwt>
    """
    # Валидация JWT токена
    if not token:
        await websocket.close(code=4001, reason="Missing token")
        return

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = int(payload.get("sub"))
    except (PyJWTError, ValueError, TypeError):
        await websocket.close(code=4001, reason="Invalid token")
        return

    # Проверяем что чат существует
    async with SessionLocal() as db:
        chat = await chat_crud.get_chat_by_exchange(db, chat_id)
        if not chat:
            await websocket.close(code=4004, reason="Chat not found")
            return
        real_chat_id = chat.id

    await manager.connect(real_chat_id, websocket)
    try:
        # Держим соединение открытым, слушаем пинги/служебные сообщения от клиента
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(real_chat_id, websocket)


@router.patch("/{chat_id}/messages/{message_id}", response_model=MessageRead)
async def edit_message(chat_id: int, message_id: int, body: MessageUpdate, db: DB):
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id, Message.id == message_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return await message_crud.edit_message(db, msg, body.content)


@router.delete("/{chat_id}/messages/{message_id}", response_model=MessageRead)
async def delete_message(chat_id: int, message_id: int, db: DB):
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id, Message.id == message_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return await message_crud.soft_delete_message(db, msg)
