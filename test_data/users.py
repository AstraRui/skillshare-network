from __future__ import annotations

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole


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
