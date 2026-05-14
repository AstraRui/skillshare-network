from __future__ import annotations

import asyncio

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models import (
    Chat,
    Exchange,
    ExchangeParticipant,
    Listing,
    ListingInterest,
    Message,
    Review,
    Skill,
    SkillCategory,
    Task,
    User,
    UserSkillsOffered,
    UserSkillsWanted,
)
from app.seed.test_data.chats import create_chats_and_messages
from app.seed.test_data.exchanges import create_exchanges, create_reviews, create_tasks
from app.seed.test_data.listings import create_interests, create_listings
from app.seed.test_data.skills import create_skills, create_user_skills
from app.seed.test_data.users import create_users


async def clear_seed_data(session: AsyncSession) -> None:
    """
    Очищает seed-данные в безопасном порядке.

    Сначала удаляются зависимые таблицы, потом основные сущности.
    Это уменьшает риск ошибок по FK/cascade при повторном запуске seed.
    """
    await session.execute(delete(Message))
    await session.execute(delete(Task))
    await session.execute(delete(Review))
    await session.execute(delete(Chat))
    await session.execute(delete(ExchangeParticipant))
    await session.execute(delete(Exchange))
    await session.execute(delete(ListingInterest))
    await session.execute(delete(Listing))
    await session.execute(delete(UserSkillsWanted))
    await session.execute(delete(UserSkillsOffered))
    await session.execute(delete(Skill))
    await session.execute(delete(SkillCategory))
    await session.execute(delete(User))
    await session.commit()


async def seed_test_data() -> None:
    async with SessionLocal() as session:
        await clear_seed_data(session)

        users = await create_users(session)
        skills = await create_skills(session)
        await create_user_skills(session, users, skills)

        listings = await create_listings(session, users)
        await create_interests(session, users, listings)

        exchanges = await create_exchanges(session, users, listings, skills)
        await create_tasks(session, exchanges)
        await create_chats_and_messages(session, exchanges)
        await create_reviews(session, exchanges)

        await session.commit()

    print("Seed test data successfully created.")


if __name__ == "__main__":
    asyncio.run(seed_test_data())
