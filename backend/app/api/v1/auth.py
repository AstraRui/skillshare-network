from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.user import TokenResponse, UserLogin, UserRegister, UserResponse
from app.services.auth import login_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])
DB = Annotated[AsyncSession, Depends(get_db_session)]


@router.post("/register", response_model=UserResponse)
async def register(data: UserRegister, db: DB) -> UserResponse:
    user = await register_user(db, data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: DB) -> TokenResponse:
    token = await login_user(db, data)
    return TokenResponse(access_token=token)
