from __future__ import annotations

import logging
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import settings
from app.db.session import get_db_session
from app.models.user import User, UserRole

logger = logging.getLogger("app.auth")
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_current_admin(
    db: DbSession,
    authorization: str | None = Header(default=None, alias="Authorization"),
) -> User:
    # проверяем что заголовок Authorization есть и начинается с Bearer
    if authorization is None or not authorization.startswith("Bearer "):
        logger.warning("Admin auth failed: missing or invalid Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.PyJWTError:
        logger.error("Admin auth failed: invalid JWT", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from None

    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Admin auth failed: JWT missing sub claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await db.scalar(select(User).where(User.id == int(user_id), User.is_deleted.is_(False)))
    if user is None:
        logger.warning("Admin auth failed: user not found user_id=%s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or blocked",
        )

    if user.role != UserRole.admin:
        logger.warning("Admin access denied for user_id=%s role=%s", user.id, user.role)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )

    return user
