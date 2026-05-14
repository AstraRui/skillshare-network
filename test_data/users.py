from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole
from app.seed.test_data.generators import (
    generate_avatar_url,
    generate_email,
    generate_full_name,
    generate_phone,
    generate_rating,
)


USERS_COUNT = 20


async def create_users(session: AsyncSession) -> list[User]:
    users: list[User] = []

    for index in range(1, USERS_COUNT + 1):
        full_name = generate_full_name()

        user = User(
            email=generate_email(index),
            phone=generate_phone(index),
            full_name=full_name,
            password_hash="test-password-hash",
            avatar_url=generate_avatar_url(full_name),
            rating=generate_rating(),
            role=UserRole.user,
            is_deleted=False,
        )

        users.append(user)
        session.add(user)

    await session.flush()
    return users
