"""
Общие зависимости FastAPI (Depends).
Импортируй отсюда во всех роутерах.
"""
from __future__ import annotations

from app.db.session import get_db_session

# Реэкспорт для удобного импорта в роутерах
__all__ = ["get_db_session"]
