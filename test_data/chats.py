from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Chat, ChatStatus, Exchange, ExchangeStatus, Message


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

        messages = [
            Message(
                chat_id=chat.id,
                exchange_id=exchange.id,
                task_id=None,
                sender_id=first_user_id,
                content="Привет! Увидел твой отклик, давай обсудим обмен навыками.",
            ),
            Message(
                chat_id=chat.id,
                exchange_id=exchange.id,
                task_id=None,
                sender_id=second_user_id,
                content="Привет! Да, мне интересно. Что удобнее разобрать сначала?",
            ),
            Message(
                chat_id=chat.id,
                exchange_id=exchange.id,
                task_id=None,
                sender_id=first_user_id,
                content="Предлагаю начать с короткого созвона и плана занятий.",
            ),
            Message(
                chat_id=chat.id,
                exchange_id=exchange.id,
                task_id=None,
                sender_id=second_user_id,
                content="Отлично, тогда договорились. Я подготовлю вопросы.",
            ),
        ]

        if exchange.status == ExchangeStatus.completed:
            messages.append(
                Message(
                    chat_id=chat.id,
                    exchange_id=exchange.id,
                    task_id=None,
                    sender_id=second_user_id,
                    content="Спасибо за обмен! Всё прошло отлично.",
                )
            )

        if exchange.status == ExchangeStatus.cancelled:
            messages.append(
                Message(
                    chat_id=chat.id,
                    exchange_id=exchange.id,
                    task_id=None,
                    sender_id=first_user_id,
                    content="Пока не получается продолжить, давай отменим сделку.",
                )
            )

        session.add_all(messages)

    await session.flush()
