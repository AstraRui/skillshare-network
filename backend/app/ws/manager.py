from __future__ import annotations

from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Хранит активные WebSocket-соединения, сгруппированные по chat_id."""

    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections[chat_id].add(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        self._connections[chat_id].discard(websocket)

    async def broadcast(self, chat_id: int, payload: dict) -> None:
        """Разослать payload всем клиентам в чате. Отключившихся убираем."""
        dead: list[WebSocket] = []
        for ws in list(self._connections[chat_id]):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections[chat_id].discard(ws)


# Синглтон — один экземпляр на весь процесс
manager = ConnectionManager()
