from fastapi import APIRouter

from .chats import router as chats_router
from .messages import router as messages_router
from .websocket import router as websocket_router

# Combine all routers into one
router = APIRouter()
router.include_router(chats_router)
router.include_router(messages_router)
router.include_router(websocket_router)
