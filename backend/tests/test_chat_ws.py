"""Тесты HTTP-эндпоинтов чата (сообщения привязаны к exchange_id)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.user import User


@pytest.fixture
def fake_user():
    user = MagicMock(spec=User)
    user.id = 42
    return user


@pytest.fixture
def fake_chat():
    chat = MagicMock()
    chat.id = 7
    chat.exchange_id = 1
    chat.status = "active"
    return chat


@pytest.fixture
async def http_client(fake_user):
    from app.api.deps import get_current_user
    from app.db.session import get_db_session

    async def override_db():
        yield AsyncMock()

    async def override_user():
        return fake_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


async def test_get_chat_by_exchange_returns_chat(http_client, fake_chat):
    with patch("app.api.v1.chat.chat_crud.get_chat_by_exchange", return_value=fake_chat):
        response = await http_client.get("/api/v1/chat/exchanges/1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == fake_chat.id
    assert data["exchange_id"] == fake_chat.exchange_id


async def test_list_messages_by_exchange(http_client, fake_message_list):
    with patch(
        "app.api.v1.chat.message_crud.get_messages_by_exchange",
        return_value=fake_message_list,
    ):
        response = await http_client.get("/api/v1/chat/exchanges/1/messages")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.fixture
def fake_message_list(fake_chat, fake_user):
    from datetime import UTC, datetime

    msg = MagicMock()
    msg.id = 1
    msg.chat_id = fake_chat.id
    msg.sender_id = fake_user.id
    msg.content = "Привет!"
    msg.media_url = None
    msg.created_at = datetime.now(UTC)
    msg.edited_at = None
    msg.is_deleted = False
    msg.task_id = None
    return [msg]
