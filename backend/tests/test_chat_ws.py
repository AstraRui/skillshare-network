"""
Тесты WebSocket-чата.
Используем starlette.testclient.TestClient — он умеет websocket_connect()
без реального сетевого соединения (всё in-process).
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.testclient import TestClient

from app.main import app
from app.models.user import User

# ── Фикстуры ────────────────────────────────────────────────────────────────


@pytest.fixture
def fake_user():
    user = MagicMock(spec=User)
    user.id = 42
    return user


@pytest.fixture
def fake_chat():
    chat = MagicMock()
    chat.id = 7  # реальный chat.id в таблице chats
    chat.exchange_id = 1  # exchange_id — то что приходит в URL
    return chat


@pytest.fixture
def fake_message(fake_chat, fake_user):
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
    return msg


# ── HTTP: POST /chat/{exchange_id}/messages ──────────────────────────────────


@pytest.fixture
async def http_client(fake_user, fake_chat, fake_message):
    """AsyncClient с замоканными зависимостями для HTTP-тестов."""
    from app.api.deps import get_current_user
    from app.db.session import get_db_session

    async def override_db():
        yield AsyncMock()

    async def override_user():
        return fake_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with (
        patch("app.api.v1.chat.chat_crud.get_chat_by_exchange", return_value=fake_chat),
        patch("app.api.v1.chat.message_crud.create_message", return_value=fake_message),
        patch("app.api.v1.chat.manager.broadcast", new_callable=AsyncMock),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            yield c

    app.dependency_overrides.clear()


async def test_send_message_returns_201(http_client, fake_message):
    response = await http_client.post(
        "/api/v1/chat/1/messages",
        json={"content": "Привет!"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Привет!"
    assert data["sender_id"] == fake_message.sender_id


async def test_send_message_broadcasts(fake_user, fake_chat, fake_message):
    """Проверяем что после сохранения вызывается broadcast."""
    from app.api.deps import get_current_user
    from app.db.session import get_db_session

    async def override_db():
        yield AsyncMock()

    async def override_user():
        return fake_user

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    broadcast_mock = AsyncMock()
    with (
        patch("app.api.v1.chat.chat_crud.get_chat_by_exchange", return_value=fake_chat),
        patch("app.api.v1.chat.message_crud.create_message", return_value=fake_message),
        patch("app.api.v1.chat.manager.broadcast", broadcast_mock),
    ):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
            await c.post("/api/v1/chat/1/messages", json={"content": "Привет!"})

    app.dependency_overrides.clear()
    broadcast_mock.assert_called_once()
    call_args = broadcast_mock.call_args
    assert call_args[0][0] == fake_chat.id  # первый позиционный — chat_id
    assert call_args[0][1]["content"] == "Привет!"


# ── WebSocket ────────────────────────────────────────────────────────────────


def test_ws_connect_and_receive():
    """
    Два клиента подключаются к одному чату.
    Первый отправляет HTTP-сообщение → второй получает его через WS.
    """
    fake_chat_obj = MagicMock()
    fake_chat_obj.id = 7
    fake_chat_obj.exchange_id = 1

    from datetime import UTC, datetime

    fake_msg_obj = MagicMock()
    fake_msg_obj.id = 1
    fake_msg_obj.chat_id = 7
    fake_msg_obj.sender_id = 99
    fake_msg_obj.content = "WS тест"
    fake_msg_obj.media_url = None
    fake_msg_obj.created_at = datetime.now(UTC)
    fake_msg_obj.edited_at = None
    fake_msg_obj.is_deleted = False

    from app.api.deps import get_current_user
    from app.db.session import get_db_session

    async def override_db():
        yield AsyncMock()

    fake_user_obj = MagicMock(spec=User)
    fake_user_obj.id = 99

    async def override_user():
        return fake_user_obj

    app.dependency_overrides[get_db_session] = override_db
    app.dependency_overrides[get_current_user] = override_user

    with (
        patch("app.api.v1.chat.chat_crud.get_chat_by_exchange", return_value=fake_chat_obj),
        patch("app.api.v1.chat.message_crud.create_message", return_value=fake_msg_obj),
        patch("app.api.v1.chat.SessionLocal") as mock_session_cls,
    ):
        # Мокаем async context manager для SessionLocal внутри WS-хендлера
        mock_db = AsyncMock()
        mock_db.execute = AsyncMock()
        mock_session_cls.return_value.__aenter__ = AsyncMock(return_value=mock_db)
        mock_session_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            TestClient(app) as client,
            client.websocket_connect("/api/v1/chat/1/ws?user_id=99") as ws2,
        ):
            # Клиент 1 отправляет HTTP POST
            r = client.post(
                "/api/v1/chat/1/messages",
                json={"content": "WS тест"},
                headers={"X-User-Id": "99"},
            )
            assert r.status_code == 201

            # Клиент 2 должен получить сообщение через WS
            data = ws2.receive_json()
            assert data["content"] == "WS тест"
            assert data["sender_id"] == 99

    app.dependency_overrides.clear()
