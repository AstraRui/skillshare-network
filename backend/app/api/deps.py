"""
Общие зависимости FastAPI (Depends).
Импортируй отсюда во всех роутерах.
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.user import User

# Реэкспорт для удобного импорта в роутерах
__all__ = ["get_db_session", "get_current_user"]


async def get_current_user(
    db: AsyncSession = Depends(get_db_session),
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
) -> User:
    """
    Временная MVP-аутентификация.
    Используй заголовок X-User-Id: <id> для подстановки текущего пользователя.
    """
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Missing X-User-Id header")

    user = await db.scalar(select(User).where(User.id == x_user_id, User.is_deleted.is_(False)))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user
