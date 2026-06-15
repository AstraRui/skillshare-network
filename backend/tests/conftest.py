"""Общие фикстуры pytest."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _skip_real_db_on_startup(monkeypatch: pytest.MonkeyPatch) -> None:
    """Тесты не требуют живой PostgreSQL при старте lifespan."""

    async def _ok() -> bool:
        return True

    monkeypatch.setattr("app.main.check_database_connection", _ok)
