from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Импортируем все модели, чтобы Alembic видел их при автогенерации миграций
from app.models import *  # noqa: E402, F401, F403
