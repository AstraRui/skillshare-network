from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

import bcrypt
import jwt
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.models.user import User
from app.schemas.user import UserLogin, UserRegister

logger = logging.getLogger("app.auth")


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), password_hash.encode())
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int, role: str) -> str:
    payload = {"sub": str(user_id), "role": role, "exp": datetime.now(UTC) + timedelta(hours=24)}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


async def register_user(db: AsyncSession, data: UserRegister) -> User:
    logger.info("Registration attempt email=%s", data.email)

    existing = await db.scalar(select(User.id).where(User.email == data.email))
    if existing is not None:
        logger.warning("Registration rejected: email already exists email=%s", data.email)
        raise HTTPException(
            status_code=409,
            detail="Пользователь с таким email уже зарегистрирован",
        )

    user = User(
        email=data.email, password_hash=hash_password(data.password), full_name=data.full_name
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as exc:
        logger.error(
            "Registration failed: database integrity error email=%s", data.email, exc_info=True
        )
        raise HTTPException(status_code=409, detail="Email уже зарегистрирован") from exc

    logger.info("User registered user_id=%d email=%s", user.id, data.email)
    return user


async def login_user(db: AsyncSession, data: UserLogin) -> str:
    logger.info("Login attempt email=%s", data.email)

    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        logger.error("Login failed: invalid credentials email=%s", data.email)
        raise HTTPException(status_code=401, detail="Неверный пароль или email")

    token = create_access_token(user.id, user.role)
    logger.info("Login successful user_id=%d role=%s JWT issued", user.id, user.role)
    return token
