from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Skill, SkillCategory, User, UserSkillsOffered, UserSkillsWanted


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

OFFERED_SKILLS_BY_USER = [
    ["Python", "FastAPI", "SQL"],
    ["Figma", "UX/UI", "Photoshop"],
    ["SQL", "Python"],
    ["Английский язык", "Немецкий язык"],
    ["SMM", "Таргетированная реклама"],
    ["Гитара", "Вокал"],
    ["Электрика", "Сборка мебели"],
    ["Видеомонтаж", "Цветокоррекция"],
    ["HTML/CSS", "Python"],
    ["SMM", "Копирайтинг"],
    ["Фотография", "Photoshop"],
    ["Английский язык", "Испанский язык"],
    ["Сантехника", "Сборка мебели"],
    ["Figma", "Photoshop"],
    ["SQL", "FastAPI"],
    ["Вокал", "Фортепиано"],
    ["Немецкий язык", "Английский язык"],
    ["Видеомонтаж", "Фотография"],
    ["Электрика", "Сантехника"],
    ["Копирайтинг", "SMM"],
]

WANTED_SKILLS_BY_USER = [
    ["Figma", "UX/UI"],
    ["Английский язык", "Копирайтинг"],
    ["Видеомонтаж", "Цветокоррекция"],
    ["Python", "HTML/CSS"],
    ["Фотография", "Photoshop"],
    ["Копирайтинг", "SMM"],
    ["Немецкий язык", "Английский язык"],
    ["FastAPI", "SQL"],
    ["Photoshop", "Figma"],
    ["Фотография", "Видеомонтаж"],
    ["SQL", "FastAPI"],
    ["Гитара", "Вокал"],
    ["HTML/CSS", "Python"],
    ["Английский язык", "Немецкий язык"],
    ["UX/UI", "Figma"],
    ["Таргетированная реклама", "SMM"],
    ["Сборка мебели", "Электрика"],
    ["Копирайтинг", "Photoshop"],
    ["Фортепиано", "Гитара"],
    ["SQL", "Python"],
]


async def create_skills(session: AsyncSession) -> dict[str, Skill]:
    categories: dict[str, SkillCategory] = {}
    skills: dict[str, Skill] = {}

    for category_name in CATEGORIES_DATA:
        category = SkillCategory(
            name=category_name,
            is_deleted=False,
            is_moderated=True,
        )
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


async def create_user_skills(
    session: AsyncSession,
    users: list[User],
    skills: dict[str, Skill],
) -> None:
    for index, user in enumerate(users):
        for skill_name in OFFERED_SKILLS_BY_USER[index]:
            session.add(
                UserSkillsOffered(
                    user_id=user.id,
                    skill_id=skills[skill_name].id,
                    level=3 + index % 3,
                    description=f"{user.full_name} может обучить навыку: {skill_name}.",
                )
            )

        for priority, skill_name in enumerate(WANTED_SKILLS_BY_USER[index], start=1):
            session.add(
                UserSkillsWanted(
                    user_id=user.id,
                    skill_id=skills[skill_name].id,
                    desired_level=2 + index % 3,
                    priority=priority,
                )
            )

    await session.flush()

