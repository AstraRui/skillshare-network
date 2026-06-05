from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.api.openapi_responses import AUTH_ERRORS_404
from app.crud import chat as chat_crud
from app.crud import message as message_crud
from app.db.session import get_db_session
from app.models import Message
from app.models.user import User
from app.schemas.chat import ChatRead
from app.schemas.message import MessageRead, MessageUpdate

router = APIRouter(prefix="/chat", tags=["chat"], responses=AUTH_ERRORS_404)
DB = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get(
    "/exchanges/{exchange_id}",
    response_model=ChatRead,
    summary="Чат сделки",
    description="Метаданные чата по ID сделки (exchange). Не найден — 404.",
)
async def get_chat(exchange_id: int, db: DB, _user: CurrentUser) -> ChatRead:
    """Возвращает чат, привязанный к сделке."""
    chat = await chat_crud.get_chat_by_exchange(db, exchange_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    return chat


@router.get(
    "/exchanges/{exchange_id}/messages",
    response_model=list[MessageRead],
    summary="Сообщения чата",
    description="История сообщений сделки (включая архивные после завершения).",
)
async def list_messages(exchange_id: int, db: DB, _user: CurrentUser) -> list[MessageRead]:
    """Список сообщений чата сделки."""
    return await message_crud.get_messages_by_exchange(db, exchange_id)


@router.patch(
    "/exchanges/{exchange_id}/messages/{message_id}",
    response_model=MessageRead,
    summary="Редактировать сообщение",
    description="Изменяет текст сообщения. Чат или сообщение не найдены — 404.",
)
async def edit_message(
    exchange_id: int, message_id: int, body: MessageUpdate, db: DB, _user: CurrentUser
) -> MessageRead:
    """Редактирование текста сообщения."""
    chat = await chat_crud.get_chat_by_exchange(db, exchange_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    result = await db.execute(
        select(Message).where(Message.chat_id == chat.id, Message.id == message_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return await message_crud.edit_message(db, msg, body.content)


@router.delete(
    "/exchanges/{exchange_id}/messages/{message_id}",
    response_model=MessageRead,
    summary="Удалить сообщение",
    description="Мягкое удаление сообщения. Возвращает обновлённую запись.",
)
async def delete_message(
    exchange_id: int, message_id: int, db: DB, _user: CurrentUser
) -> MessageRead:
    """Мягкое удаление сообщения в чате сделки."""
    chat = await chat_crud.get_chat_by_exchange(db, exchange_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Чат не найден")
    result = await db.execute(
        select(Message).where(Message.chat_id == chat.id, Message.id == message_id)
    )
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Сообщение не найдено")
    return await message_crud.soft_delete_message(db, msg)
