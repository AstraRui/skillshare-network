from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Exchange,
    ExchangeParticipant,
    ExchangeStatus,
    Listing,
    Review,
    Skill,
    Task,
    User,
)


EXCHANGES_DATA = [
    {
        "listing": 0,
        "initiator": 0,
        "partner": 1,
        "status": ExchangeStatus.active,
        "initiator_gives": "Python",
        "initiator_gets": "Figma",
        "partner_gives": "Figma",
        "partner_gets": "Python",
    },
    {
        "listing": 1,
        "initiator": 1,
        "partner": 3,
        "status": ExchangeStatus.discussion,
        "initiator_gives": "Figma",
        "initiator_gets": "Английский язык",
        "partner_gives": "Английский язык",
        "partner_gets": "Figma",
    },
    {
        "listing": 2,
        "initiator": 2,
        "partner": 7,
        "status": ExchangeStatus.completed,
        "initiator_gives": "SQL",
        "initiator_gets": "Видеомонтаж",
        "partner_gives": "Видеомонтаж",
        "partner_gets": "SQL",
    },
    {
        "listing": 3,
        "initiator": 3,
        "partner": 0,
        "status": ExchangeStatus.completed,
        "initiator_gives": "Английский язык",
        "initiator_gets": "HTML/CSS",
        "partner_gives": "HTML/CSS",
        "partner_gets": "Английский язык",
    },
    {
        "listing": 4,
        "initiator": 4,
        "partner": 17,
        "status": ExchangeStatus.active,
        "initiator_gives": "SMM",
        "initiator_gets": "Фотография",
        "partner_gives": "Фотография",
        "partner_gets": "SMM",
    },
    {
        "listing": 6,
        "initiator": 6,
        "partner": 16,
        "status": ExchangeStatus.cancelled,
        "initiator_gives": "Электрика",
        "initiator_gets": "Немецкий язык",
        "partner_gives": "Немецкий язык",
        "partner_gets": "Электрика",
    },
    {
        "listing": 7,
        "initiator": 7,
        "partner": 14,
        "status": ExchangeStatus.active,
        "initiator_gives": "Видеомонтаж",
        "initiator_gets": "FastAPI",
        "partner_gives": "FastAPI",
        "partner_gets": "Видеомонтаж",
    },
    {
        "listing": 9,
        "initiator": 9,
        "partner": 10,
        "status": ExchangeStatus.completed,
        "initiator_gives": "SMM",
        "initiator_gets": "Фотография",
        "partner_gives": "Фотография",
        "partner_gets": "SMM",
    },
]

TASK_TITLES = [
    "Провести первый созвон",
    "Согласовать план обмена",
    "Отправить учебные материалы",
    "Выполнить первое практическое задание",
    "Проверить результат и дать обратную связь",
]


async def create_exchanges(
    session: AsyncSession,
    users: list[User],
    listings: list[Listing],
    skills: dict[str, Skill],
) -> list[Exchange]:
    exchanges: list[Exchange] = []

    for item in EXCHANGES_DATA:
        is_completed = item["status"] == ExchangeStatus.completed

        exchange = Exchange(
            initiator_id=users[item["initiator"]].id,
            listing_id=listings[item["listing"]].id,
            status=item["status"],
            is_chain=False,
            completed_at=datetime.now(UTC) if is_completed else None,
            completed_by_initiator=is_completed,
            completed_by_partner=is_completed,
            is_deleted=False,
        )
        session.add(exchange)
        await session.flush()

        session.add_all(
            [
                ExchangeParticipant(
                    exchange_id=exchange.id,
                    user_id=users[item["initiator"]].id,
                    gives_skill_id=skills[item["initiator_gives"]].id,
                    gets_skill_id=skills[item["initiator_gets"]].id,
                    position=1,
                ),
                ExchangeParticipant(
                    exchange_id=exchange.id,
                    user_id=users[item["partner"]].id,
                    gives_skill_id=skills[item["partner_gives"]].id,
                    gets_skill_id=skills[item["partner_gets"]].id,
                    position=2,
                ),
            ]
        )

        exchanges.append(exchange)

    await session.flush()
    return exchanges


async def create_tasks(session: AsyncSession, exchanges: list[Exchange]) -> None:
    for exchange in exchanges:
        await session.refresh(exchange, attribute_names=["participants"])
        participant_ids = [participant.user_id for participant in exchange.participants]

        if not participant_ids:
            continue

        if exchange.status == ExchangeStatus.cancelled:
            statuses = ["cancelled", "cancelled"]
            titles = TASK_TITLES[:2]
        elif exchange.status == ExchangeStatus.completed:
            statuses = ["done", "done", "done", "done", "done"]
            titles = TASK_TITLES
        else:
            statuses = ["done", "in_progress", "todo"]
            titles = TASK_TITLES[:3]

        for index, title in enumerate(titles):
            session.add(
                Task(
                    exchange_id=exchange.id,
                    assignee_id=participant_ids[index % len(participant_ids)],
                    title=title,
                    status=statuses[index],
                )
            )

    await session.flush()


async def create_reviews(session: AsyncSession, exchanges: list[Exchange]) -> None:
    for exchange in exchanges:
        if exchange.status != ExchangeStatus.completed:
            continue

        await session.refresh(exchange, attribute_names=["participants"])
        participant_ids = [participant.user_id for participant in exchange.participants]

        if len(participant_ids) < 2:
            continue

        first_user_id = participant_ids[0]
        second_user_id = participant_ids[1]

        session.add_all(
            [
                Review(
                    exchange_id=exchange.id,
                    reviewer_id=first_user_id,
                    reviewed_id=second_user_id,
                    rating=5,
                    comment="Отличный обмен навыками. Всё объяснено понятно и по делу.",
                    is_deleted=False,
                    is_moderated=True,
                    is_hidden=False,
                ),
                Review(
                    exchange_id=exchange.id,
                    reviewer_id=second_user_id,
                    reviewed_id=first_user_id,
                    rating=5,
                    comment="Хороший участник, быстро отвечает и выполняет договоренности.",
                    is_deleted=False,
                    is_moderated=True,
                    is_hidden=False,
                ),
            ]
        )

    await session.flush()
