from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Message


async def get_messages_by_exchange(db: AsyncSession, exchange_id: int) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.exchange_id == exchange_id, Message.is_deleted.is_(False))
        .order_by(Message.created_at)
    )
    return list(result.scalars().all())


async def create_exchange_message(
    db: AsyncSession,
    exchange_id: int,
    sender_id: int,
    content: str | None,
    media_url: str | None = None,
) -> Message:
    msg = Message(
        exchange_id=exchange_id,
        sender_id=sender_id,
        content=content,
        media_url=media_url,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg


async def edit_message(db: AsyncSession, message: Message, content: str) -> Message:
    message.content = content
    await db.commit()
    await db.refresh(message)
    return message


async def soft_delete_message(db: AsyncSession, message: Message) -> Message:
    message.is_deleted = True
    await db.commit()
    await db.refresh(message)
    return message
