from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.api.openapi_responses import AUTH_ERRORS, PUBLIC_ERRORS, RESP_409
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"], responses=PUBLIC_ERRORS)
DB = Annotated[AsyncSession, Depends(get_db_session)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация пользователя",
    description="Создаёт нового пользователя. Пароль — минимум 10 символов.",
    responses={**PUBLIC_ERRORS, 409: RESP_409},
)
async def register(data: UserRegister, db: DB) -> UserResponse:
    """Регистрация нового аккаунта. При дубликате email — 409 Conflict."""
    user = await register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Вход в систему",
    description="Проверяет email и пароль, возвращает JWT access_token для заголовка Authorization.",
    responses={**AUTH_ERRORS, 400: PUBLIC_ERRORS[400]},
)
async def login(data: UserLogin, db: DB) -> TokenResponse:
    """Успешный вход — 200 OK с `access_token`. Неверные данные — 400 Bad Request."""
    token = await login_user(db, data)
    return TokenResponse(access_token=token)
