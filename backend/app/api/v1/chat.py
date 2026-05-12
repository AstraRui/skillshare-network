from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.crud import chat as chat_crud
from app.crud import message as message_crud
from app.db.session import get_db_session
from app.models import Chat, Message
from app.schemas.chat import ChatRead
from app.schemas.message import MessageRead, MessageCreate, MessageUpdate

router = APIRouter(prefix="/chat", tags=["chat"])
DB = Annotated[AsyncSession, Depends(get_db_session)]

@router.get("/exchanges/{exchange_id}", response_model=ChatRead)
async def get_chat(exchange_id: int, db: DB):
    chat = await chat_crud.get_chat_by_exchange(db, exchange_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat

@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_messages(chat_id: int, db: DB):
    return await message_crud.get_messages(db, chat_id)

# Доделать после слива с авторизацией
# @router.post("/{chat_id}/messages", response_model=ChatRead, status_code=201)
# async def send_message(chat_id: int, body: MessageCreate, db: DB):
#
#

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