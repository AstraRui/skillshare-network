from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.exc import IntegrityError

from app.api.errors import (
    http_exception_handler,
    integrity_error_handler,
    request_validation_handler,
)
from app.api.router import router as api_router
from app.core.settings import settings
from app.db.session import check_database_connection, engine
from app.logging.logging_config import setup_logging
from app.logging.logging_middleware import logging_middleware

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

OPENAPI_TAGS = [
    {"name": "health", "description": "Проверка доступности API и подключения к БД."},
    {"name": "Auth", "description": "Регистрация и вход. Возвращает JWT access_token."},
    {"name": "users", "description": "Профиль текущего пользователя, навыки, пароль, отзывы."},
    {"name": "skills", "description": "Справочник категорий и навыков."},
    {"name": "listings", "description": "Объявления об обмене навыками и отклики."},
    {"name": "exchanges", "description": "Сделки (обмены), сообщения и отзывы внутри сделки."},
    {"name": "matches", "description": "Рекомендации пар для обмена (матчмейкинг)."},
    {"name": "chat", "description": "Чат сделки: просмотр, редактирование и удаление сообщений."},
    {"name": "Admin", "description": "Модерация пользователей, объявлений, сделок и чатов (роль admin)."},
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    startup_logger = logging.getLogger("app.startup")
    startup_logger.info(
        "Starting %s environment=%s",
        settings.app_name,
        settings.environment,
    )

    if not await check_database_connection():
        startup_logger.warning(
            "Application started without database — API requests may return errors"
        )

    yield

    startup_logger.info("Shutting down %s", settings.app_name)
    await engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        description=(
            "REST API платформы SkillShare Network. "
            "Большинство эндпоинтов требуют заголовок `Authorization: Bearer <JWT>`. "
            "Получите токен через `POST /api/v1/auth/login`."
        ),
        version="1.0.0",
        lifespan=lifespan,
        openapi_tags=OPENAPI_TAGS,
    )

    def custom_openapi() -> dict:
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
            tags=OPENAPI_TAGS,
        )
        schema.setdefault("components", {}).setdefault("securitySchemes", {})[
            "BearerAuth"
        ] = {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT из ответа POST /api/v1/auth/login",
        }
        app.openapi_schema = schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]

    app.middleware("http")(logging_middleware)

    app.add_exception_handler(RequestValidationError, request_validation_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    app.include_router(api_router, prefix="/api")

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    async def index() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
