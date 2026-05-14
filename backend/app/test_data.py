from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.models import (
    Chat,
    ChatStatus,
    Exchange,
    ExchangeParticipant,
    ExchangeStatus,
    Listing,
    ListingInterest,
    ListingInterestStatus,
    ListingStatus,
    Message,
    Review,
    Skill,
    SkillCategory,
    Task,
    User,
    UserRole,
    UserSkillsOffered,
    UserSkillsWanted,
)


USERS_DATA = [
    ("ivan.petrov@example.com", "+79990000001", "Иван Петров", Decimal("4.80")),
    ("anna.smirnova@example.com", "+79990000002", "Анна Смирнова", Decimal("4.95")),
    ("maksim.ivanov@example.com", "+79990000003", "Максим Иванов", Decimal("4.70")),
    ("elena.kuznetsova@example.com", "+79990000004", "Елена Кузнецова", Decimal("4.90")),
    ("dmitry.sokolov@example.com", "+79990000005", "Дмитрий Соколов", Decimal("4.60")),
    ("olga.popova@example.com", "+79990000006", "Ольга Попова", Decimal("4.85")),
    ("sergey.volkov@example.com", "+79990000007", "Сергей Волков", Decimal("4.50")),
    ("maria.fedorova@example.com", "+79990000008", "Мария Фёдорова", Decimal("4.75")),
    ("alexey.morozov@example.com", "+79990000009", "Алексей Морозов", Decimal("4.65")),
    ("natalia.orlova@example.com", "+79990000010", "Наталья Орлова", Decimal("4.88")),
    ("artem.lebedev@example.com", "+79990000011", "Артём Лебедев", Decimal("4.40")),
    ("sofia.egorova@example.com", "+79990000012", "София Егорова", Decimal("4.92")),
    ("kirill.nikitin@example.com", "+79990000013", "Кирилл Никитин", Decimal("4.55")),
    ("alina.zaytseva@example.com", "+79990000014", "Алина Зайцева", Decimal("4.78")),
    ("roman.belov@example.com", "+79990000015", "Роман Белов", Decimal("4.35")),
    ("daria.vasileva@example.com", "+79990000016", "Дарья Васильева", Decimal("4.82")),
    ("nikita.karpov@example.com", "+79990000017", "Никита Карпов", Decimal("4.58")),
    ("polina.mikhailova@example.com", "+79990000018", "Полина Михайлова", Decimal("4.93")),
    ("egor.tarasenko@example.com", "+79990000019", "Егор Тарасенко", Decimal("4.47")),
    ("victoria.andreeva@example.com", "+79990000020", "Виктория Андреева", Decimal("4.86")),
]

CATEGORIES_DATA = [
    "IT и программирование",
    "Дизайн",
    "Иностранные языки",
    "Музыка",
    "Маркетинг",
    "Фото и видео",
    "Ремонт и быт",
]

SKILLS_DATA = {
    "IT и программирование": [
        ("Python", "Основы Python, backend-разработка, автоматизация."),
        ("HTML/CSS", "Верстка страниц и адаптивный дизайн."),
        ("FastAPI", "Создание API на Python."),
        ("SQL", "Работа с базами данных и запросами."),
    ],
    "Дизайн": [
        ("Figma", "Дизайн интерфейсов и прототипирование."),
        ("Photoshop", "Обработка изображений и графика."),
        ("UX/UI", "Проектирование удобных интерфейсов."),
    ],
    "Иностранные языки": [
        ("Английский язык", "Разговорный английский и грамматика."),
        ("Немецкий язык", "Базовый и средний уровень немецкого."),
        ("Испанский язык", "Основы испанского языка."),
    ],
    "Музыка": [
        ("Гитара", "Обучение игре на гитаре."),
        ("Вокал", "Постановка голоса и практика пения."),
        ("Фортепиано", "Базовое обучение игре на фортепиано."),
    ],
    "Маркетинг": [
        ("SMM", "Продвижение в социальных сетях."),
        ("Копирайтинг", "Написание продающих и информационных текстов."),
        ("Таргетированная реклама", "Настройка рекламы в соцсетях."),
    ],
    "Фото и видео": [
        ("Видеомонтаж", "Монтаж роликов, Reels, YouTube-видео."),
        ("Фотография", "Основы съемки и композиции."),
        ("Цветокоррекция", "Обработка видео и фото по цвету."),
    ],
    "Ремонт и быт": [
        ("Электрика", "Базовые бытовые работы с электрикой."),
        ("Сантехника", "Мелкий ремонт сантехники."),
        ("Сборка мебели", "Сборка шкафов, столов и другой мебели."),
    ],
}

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


async def clear_seed_data(session: AsyncSession) -> None:
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


async def create_users(session: AsyncSession) -> list[User]:
    users: list[User] = []
    for email, phone, full_name, rating in USERS_DATA:
        user = User(
            email=email,
            phone=phone,
            full_name=full_name,
            password_hash="test-password-hash",
            avatar_url=f"https://api.dicebear.com/7.x/initials/svg?seed={full_name}",
            rating=rating,
            role=UserRole.user,
            is_deleted=False,
        )
        users.append(user)
        session.add(user)
    await session.flush()
    return users


async def create_skills(session: AsyncSession) -> dict[str, Skill]:
    categories: dict[str, SkillCategory] = {}
    skills: dict[str, Skill] = {}
    for category_name in CATEGORIES_DATA:
        category = SkillCategory(name=category_name, is_deleted=False, is_moderated=True)
        session.add(category)
        categories[category_name] = category
    await session.flush()

    for category_name, skill_items in SKILLS_DATA.items():
        category = categories[category_name]
        for skill_name, description in skill_items:
            skill = Skill(
                name=skill_name,
                category_id=category.id,
                description=description,
                is_deleted=False,
                is_moderated=True,
            )
            session.add(skill)
            skills[skill_name] = skill
    await session.flush()
    return skills


async def create_user_skills(session: AsyncSession, users: list[User], skills: dict[str, Skill]) -> None:
    offered_map = [
        ["Python", "FastAPI", "SQL"], ["Figma", "UX/UI", "Photoshop"], ["SQL", "Python"],
        ["Английский язык", "Немецкий язык"], ["SMM", "Таргетированная реклама"], ["Гитара", "Вокал"],
        ["Электрика", "Сборка мебели"], ["Видеомонтаж", "Цветокоррекция"], ["HTML/CSS", "Python"],
        ["SMM", "Копирайтинг"], ["Фотография", "Photoshop"], ["Английский язык", "Испанский язык"],
        ["Сантехника", "Сборка мебели"], ["Figma", "Photoshop"], ["SQL", "FastAPI"],
        ["Вокал", "Фортепиано"], ["Немецкий язык", "Английский язык"], ["Видеомонтаж", "Фотография"],
        ["Электрика", "Сантехника"], ["Копирайтинг", "SMM"],
    ]
    wanted_map = [
        ["Figma", "UX/UI"], ["Английский язык", "Копирайтинг"], ["Видеомонтаж", "Цветокоррекция"],
        ["Python", "HTML/CSS"], ["Фотография", "Photoshop"], ["Копирайтинг", "SMM"],
        ["Немецкий язык", "Английский язык"], ["FastAPI", "SQL"], ["Photoshop", "Figma"],
        ["Фотография", "Видеомонтаж"], ["SQL", "FastAPI"], ["Гитара", "Вокал"],
        ["HTML/CSS", "Python"], ["Английский язык", "Немецкий язык"], ["UX/UI", "Figma"],
        ["Таргетированная реклама", "SMM"], ["Сборка мебели", "Электрика"], ["Копирайтинг", "Photoshop"],
        ["Фортепиано", "Гитара"], ["SQL", "Python"],
    ]
    for index, user in enumerate(users):
        for skill_name in offered_map[index]:
            session.add(UserSkillsOffered(
                user_id=user.id,
                skill_id=skills[skill_name].id,
                level=3 + index % 3,
                description=f"{user.full_name} может обучить навыку: {skill_name}.",
            ))
        for priority, skill_name in enumerate(wanted_map[index], start=1):
            session.add(UserSkillsWanted(
                user_id=user.id,
                skill_id=skills[skill_name].id,
                desired_level=2 + index % 3,
                priority=priority,
            ))
    await session.flush()


async def create_listings(session: AsyncSession, users: list[User]) -> list[Listing]:
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


async def create_interests(session: AsyncSession, users: list[User], listings: list[Listing]) -> None:
    interest_data = [
        (0, 1, ListingInterestStatus.accepted), (0, 4, ListingInterestStatus.pending),
        (1, 3, ListingInterestStatus.accepted), (1, 8, ListingInterestStatus.rejected),
        (2, 7, ListingInterestStatus.accepted), (2, 10, ListingInterestStatus.pending),
        (3, 0, ListingInterestStatus.accepted), (4, 17, ListingInterestStatus.accepted),
        (5, 19, ListingInterestStatus.pending), (6, 16, ListingInterestStatus.accepted),
        (7, 14, ListingInterestStatus.accepted), (8, 13, ListingInterestStatus.pending),
        (9, 10, ListingInterestStatus.accepted), (9, 15, ListingInterestStatus.withdrawn),
    ]
    for listing_index, responder_index, status in interest_data:
        session.add(ListingInterest(
            listing_id=listings[listing_index].id,
            responder_id=users[responder_index].id,
            message="Здравствуйте! Мне интересно ваше предложение. Готов обсудить обмен навыками.",
            status=status,
        ))
    await session.flush()


async def create_exchanges(session: AsyncSession, users: list[User], listings: list[Listing], skills: dict[str, Skill]) -> list[Exchange]:
    exchanges_data = [
        (0, 0, 1, ExchangeStatus.active, "Python", "Figma", "Figma", "Python"),
        (1, 1, 3, ExchangeStatus.discussion, "Figma", "Английский язык", "Английский язык", "Figma"),
        (2, 2, 7, ExchangeStatus.completed, "SQL", "Видеомонтаж", "Видеомонтаж", "SQL"),
        (3, 3, 0, ExchangeStatus.completed, "Английский язык", "HTML/CSS", "HTML/CSS", "Английский язык"),
        (4, 4, 17, ExchangeStatus.active, "SMM", "Фотография", "Фотография", "SMM"),
        (6, 6, 16, ExchangeStatus.cancelled, "Электрика", "Немецкий язык", "Немецкий язык", "Электрика"),
        (7, 7, 14, ExchangeStatus.active, "Видеомонтаж", "FastAPI", "FastAPI", "Видеомонтаж"),
        (9, 9, 10, ExchangeStatus.completed, "SMM", "Фотография", "Фотография", "SMM"),
    ]
    exchanges: list[Exchange] = []
    for listing_idx, initiator_idx, partner_idx, status, init_gives, init_gets, partner_gives, partner_gets in exchanges_data:
        is_completed = status == ExchangeStatus.completed
        exchange = Exchange(
            initiator_id=users[initiator_idx].id,
            listing_id=listings[listing_idx].id,
            status=status,
            is_chain=False,
            completed_at=datetime.now(UTC) if is_completed else None,
            completed_by_initiator=is_completed,
            completed_by_partner=is_completed,
            is_deleted=False,
        )
        session.add(exchange)
        await session.flush()
        session.add_all([
            ExchangeParticipant(
                exchange_id=exchange.id,
                user_id=users[initiator_idx].id,
                gives_skill_id=skills[init_gives].id,
                gets_skill_id=skills[init_gets].id,
                position=1,
            ),
            ExchangeParticipant(
                exchange_id=exchange.id,
                user_id=users[partner_idx].id,
                gives_skill_id=skills[partner_gives].id,
                gets_skill_id=skills[partner_gets].id,
                position=2,
            ),
        ])
        exchanges.append(exchange)
    await session.flush()
    return exchanges


async def create_chats_messages_tasks_reviews(session: AsyncSession, exchanges: list[Exchange]) -> None:
    task_titles = [
        "Провести первый созвон",
        "Согласовать план обмена",
        "Отправить учебные материалы",
        "Выполнить первое практическое задание",
        "Проверить результат и дать обратную связь",
    ]

    for exchange in exchanges:
        await session.refresh(exchange, attribute_names=["participants"])
        participant_ids = [participant.user_id for participant in exchange.participants]
        if len(participant_ids) < 2:
            continue

        first_user_id, second_user_id = participant_ids[0], participant_ids[1]
        is_closed = exchange.status in {ExchangeStatus.completed, ExchangeStatus.cancelled}
        chat = Chat(
            exchange_id=exchange.id,
            status=ChatStatus.closed if is_closed else ChatStatus.active,
        )
        session.add(chat)
        await session.flush()

        session.add_all([
            Message(chat_id=chat.id, exchange_id=exchange.id, task_id=None, sender_id=first_user_id,
                    content="Привет! Увидел твой отклик, давай обсудим обмен навыками."),
            Message(chat_id=chat.id, exchange_id=exchange.id, task_id=None, sender_id=second_user_id,
                    content="Привет! Да, мне интересно. Что удобнее разобрать сначала?"),
            Message(chat_id=chat.id, exchange_id=exchange.id, task_id=None, sender_id=first_user_id,
                    content="Предлагаю начать с короткого созвона и плана занятий."),
            Message(chat_id=chat.id, exchange_id=exchange.id, task_id=None, sender_id=second_user_id,
                    content="Отлично, тогда договорились. Я подготовлю вопросы."),
        ])

        if exchange.status == ExchangeStatus.completed:
            statuses = ["done", "done", "done", "done", "done"]
            titles = task_titles
            session.add_all([
                Review(exchange_id=exchange.id, reviewer_id=first_user_id, reviewed_id=second_user_id,
                       rating=5, comment="Отличный обмен навыками. Все объяснено понятно и по делу.",
                       is_deleted=False, is_moderated=True, is_hidden=False),
                Review(exchange_id=exchange.id, reviewer_id=second_user_id, reviewed_id=first_user_id,
                       rating=5, comment="Хороший участник, быстро отвечает и выполняет договоренности.",
                       is_deleted=False, is_moderated=True, is_hidden=False),
            ])
        elif exchange.status == ExchangeStatus.cancelled:
            statuses = ["cancelled", "cancelled"]
            titles = task_titles[:2]
        else:
            statuses = ["done", "in_progress", "todo"]
            titles = task_titles[:3]

        for index, title in enumerate(titles):
            session.add(Task(
                exchange_id=exchange.id,
                assignee_id=participant_ids[index % len(participant_ids)],
                title=title,
                status=statuses[index],
            ))

    await session.flush()


async def seed_test_data() -> None:
    async with SessionLocal() as session:
        await clear_seed_data(session)
        users = await create_users(session)
        skills = await create_skills(session)
        await create_user_skills(session, users, skills)
        listings = await create_listings(session, users)
        await create_interests(session, users, listings)
        exchanges = await create_exchanges(session, users, listings, skills)
        await create_chats_messages_tasks_reviews(session, exchanges)
        await session.commit()
    print("Seed test data successfully created.")


if __name__ == "__main__":
    asyncio.run(seed_test_data())
