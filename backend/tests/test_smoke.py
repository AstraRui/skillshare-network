"""Smoke-тесты: проверяем что приложение стартует и базовые эндпоинты отвечают."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app


@pytest.fixture
def mock_db():
    """Мок сессии БД — не нужна реальная БД для smoke-тестов."""
    session = AsyncMock(spec=AsyncSession)
    session.execute = AsyncMock(return_value=AsyncMock(scalar=lambda: 1))
    return session


@pytest.fixture
async def client(mock_db):
    from app.db.session import get_db_session

    async def override_db():
        yield mock_db

    app.dependency_overrides[get_db_session] = override_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


async def test_health(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
