from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router as api_router
from app.core.settings import settings
from app.web.templates import templates

BASE_DIR = Path(__file__).resolve().parent


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(api_router, prefix="/api")

    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

    @app.get("/", response_class=HTMLResponse)
    async def index(request: Request) -> HTMLResponse:
        return templates.TemplateResponse("index.html", {"request": request})

    @app.websocket("/ws/chat")
    async def ws_chat(websocket: WebSocket) -> None:
        await websocket.accept()
        try:
            while True:
                msg = await websocket.receive_text()
                await websocket.send_text(f"echo: {msg}")
        except WebSocketDisconnect:
            return

    return app


app = create_app()
