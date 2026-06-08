"""Health-check эндпоинт — проверяет БД и Redis."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session

router = APIRouter(prefix="/health", tags=["health"])

logger = logging.getLogger("app.database")
DB = Annotated[AsyncSession, Depends(get_db_session)]


@router.get(
    "",
    summary="Healthcheck",
    description="Проверяет доступность API и соединение с PostgreSQL. Аутентификация не требуется.",
    responses={
        200: {
            "description": "Сервис доступен (200 OK)",
            "content": {
                "application/json": {
                    "example": {"status": "ok", "db": "ok"},
                }
            },
        },
    },
)
async def health(db: DB) -> dict[str, str]:
    """Возвращает `status: ok` и состояние БД (`db: ok` или описание ошибки)."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        logger.critical("Health check: PostgreSQL unavailable", exc_info=True)
        db_status = f"error: {e}"
    return {"status": "ok", "db": db_status}
