"""Chat connection manager for WebSocket handling."""

from typing import Any

from fastapi import WebSocket


class ChatConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, chat_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.setdefault(chat_id, []).append(websocket)

    def disconnect(self, chat_id: int, websocket: WebSocket) -> None:
        connections = self.active_connections.get(chat_id, [])
        if websocket in connections:
            connections.remove(websocket)
        if not connections and chat_id in self.active_connections:
            del self.active_connections[chat_id]

    async def broadcast(self, chat_id: int, payload: dict[str, Any]) -> None:
        connections = list(self.active_connections.get(chat_id, []))
        for connection in connections:
            await connection.send_json(payload)


manager = ChatConnectionManager()