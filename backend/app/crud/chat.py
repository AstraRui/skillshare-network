from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chat, ChatStatus


async def create_chat(db: AsyncSession, exchange_id: int) -> Chat:
    chat = Chat(exchange_id=exchange_id)
    db.add(chat)
    await db.flush()
    await db.refresh(chat)
    return chat


async def get_chat_by_exchange(db: AsyncSession, exchange_id: int) -> Chat | None:
    result = await db.execute(select(Chat).where(Chat.exchange_id == exchange_id))
    return result.scalar_one_or_none()


async def close_chat(db: AsyncSession, chat: Chat) -> Chat:
    chat.status = ChatStatus.closed
    await db.flush()
    await db.refresh(chat)
    return chat
