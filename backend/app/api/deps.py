"""
Общие зависимости FastAPI (Depends).
Импортируй отсюда во всех роутерах.
"""
from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

# Алиас для удобного использования в роутерах:
# async def endpoint(db: DB) -> ...:
DB = Depends(get_db_session)


async def get_db(session: AsyncSession = Depends(get_db_session)) -> AsyncGenerator[AsyncSession, None]:
    yield session
