from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chat, ChatStatus, Exchange, ExchangeStatus, Message
from app.seed.test_data.generators import (
    generate_cancelled_message,
    generate_chat_messages,
    generate_completed_message,
)


async def create_chats_and_messages(
    session: AsyncSession,
    exchanges: list[Exchange],
) -> None:
    for exchange in exchanges:
        await session.refresh(exchange, attribute_names=["participants"])
        participant_ids = [participant.user_id for participant in exchange.participants]

        if len(participant_ids) < 2:
            continue

        first_user_id = participant_ids[0]
        second_user_id = participant_ids[1]
        is_closed = exchange.status in {ExchangeStatus.completed, ExchangeStatus.cancelled}

        chat = Chat(
            exchange_id=exchange.id,
            status=ChatStatus.closed if is_closed else ChatStatus.active,
        )
        session.add(chat)
        await session.flush()

        messages: list[Message] = []

        for index, content in enumerate(generate_chat_messages()):
            sender_id = first_user_id if index % 2 == 0 else second_user_id
            messages.append(
                Message(
                    chat_id=chat.id,
                    exchange_id=exchange.id,
                    task_id=None,
                    sender_id=sender_id,
                    content=content,
                )
            )

        if exchange.status == ExchangeStatus.completed:
            messages.append(
                Message(
                    chat_id=chat.id,
                    exchange_id=exchange.id,
                    task_id=None,
                    sender_id=second_user_id,
                    content=generate_completed_message(),
                )
            )

        if exchange.status == ExchangeStatus.cancelled:
            messages.append(
                Message(
                    chat_id=chat.id,
                    exchange_id=exchange.id,
                    task_id=None,
                    sender_id=first_user_id,
                    content=generate_cancelled_message(),
                )
            )

        session.add_all(messages)

    await session.flush()
