from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Listing,
    ListingInterest,
    ListingInterestStatus,
    ListingStatus,
    User,
)


LISTINGS_DATA = [
    {
        "author": 0,
        "title": "Научу Python за помощь с Figma",
        "description": "Помогу разобраться с основами Python, функциями, классами и простыми API.",
        "offering": "Python, FastAPI, SQL",
        "seeking": "Figma и UX/UI для оформления личного проекта",
    },
    {
        "author": 1,
        "title": "Дизайн интерфейса в обмен на английский",
        "description": "Могу сделать прототип сайта или мобильного приложения в Figma.",
        "offering": "Figma, UX/UI",
        "seeking": "Разговорная практика английского языка",
    },
    {
        "author": 2,
        "title": "Помогу с SQL и базами данных",
        "description": "Объясню таблицы, связи, JOIN, индексы и простые запросы.",
        "offering": "SQL",
        "seeking": "Видеомонтаж для коротких роликов",
    },
    {
        "author": 3,
        "title": "Английский язык для начинающих",
        "description": "Провожу разговорную практику и объясняю грамматику простым языком.",
        "offering": "Английский язык",
        "seeking": "Python или HTML/CSS",
    },
    {
        "author": 4,
        "title": "Настрою таргетированную рекламу",
        "description": "Помогу с базовой стратегией, аудиторией и рекламными креативами.",
        "offering": "Таргетированная реклама, SMM",
        "seeking": "Фотография и цветокоррекция",
    },
    {
        "author": 5,
        "title": "Научу играть на гитаре",
        "description": "Подберем простые песни, разберем аккорды и ритм.",
        "offering": "Гитара",
        "seeking": "Копирайтинг и оформление текстов",
    },
    {
        "author": 6,
        "title": "Мелкий бытовой ремонт",
        "description": "Подскажу по электрике, сборке мебели и мелким работам дома.",
        "offering": "Электрика, сборка мебели",
        "seeking": "Немецкий язык",
    },
    {
        "author": 7,
        "title": "Сделаю монтаж видео",
        "description": "Помогу смонтировать короткие ролики для соцсетей.",
        "offering": "Видеомонтаж, цветокоррекция",
        "seeking": "FastAPI и backend-разработка",
    },
    {
        "author": 8,
        "title": "HTML/CSS для старта",
        "description": "Объясню верстку, flexbox, grid и адаптив.",
        "offering": "HTML/CSS",
        "seeking": "Photoshop",
    },
    {
        "author": 9,
        "title": "Помогу с SMM-стратегией",
        "description": "Разберем контент-план, оформление профиля и продвижение.",
        "offering": "SMM, копирайтинг",
        "seeking": "Фотография",
    },
]

INTERESTS_DATA = [
    (0, 1, ListingInterestStatus.accepted),
    (0, 4, ListingInterestStatus.pending),
    (1, 3, ListingInterestStatus.accepted),
    (1, 8, ListingInterestStatus.rejected),
    (2, 7, ListingInterestStatus.accepted),
    (2, 10, ListingInterestStatus.pending),
    (3, 0, ListingInterestStatus.accepted),
    (4, 17, ListingInterestStatus.accepted),
    (5, 19, ListingInterestStatus.pending),
    (6, 16, ListingInterestStatus.accepted),
    (7, 14, ListingInterestStatus.accepted),
    (8, 13, ListingInterestStatus.pending),
    (9, 10, ListingInterestStatus.accepted),
    (9, 15, ListingInterestStatus.withdrawn),
]


async def create_listings(
    session: AsyncSession,
    users: list[User],
) -> list[Listing]:
    listings: list[Listing] = []

    for item in LISTINGS_DATA:
        listing = Listing(
            author_id=users[item["author"]].id,
            title=item["title"],
            description=item["description"],
            offering_summary=item["offering"],
            seeking_summary=item["seeking"],
            status=ListingStatus.published,
        )
        listings.append(listing)
        session.add(listing)

    await session.flush()
    return listings


async def create_interests(
    session: AsyncSession,
    users: list[User],
    listings: list[Listing],
) -> None:
    for listing_index, responder_index, status in INTERESTS_DATA:
        session.add(
            ListingInterest(
                listing_id=listings[listing_index].id,
                responder_id=users[responder_index].id,
                message="Здравствуйте! Мне интересно ваше предложение. Готов обсудить обмен навыками.",
                status=status,
            )
        )

    await session.flush()
