#!/usr/bin/env python3
"""
Скрипт инициализации БД: создаёт таблицы через Alembic.
Запуск: uv run python init_db.py
"""
from __future__ import annotations

import asyncio

from sqlalchemy import text

from app.core.settings import settings
from app.db.session import engine


async def init_db() -> None:
    print(f"🔌 Подключение к БД: {settings.database_url}")
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT version()"))
        version = result.scalar()
        print(f"✅ PostgreSQL подключён: {version}")
    
    print("✅ БД готова. Запустите миграции: uv run alembic upgrade head")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_db())
