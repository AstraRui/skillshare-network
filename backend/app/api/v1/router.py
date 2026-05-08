"""Агрегирует все v1 роутеры в один."""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import auth, chat, health, matches, skills, users

router = APIRouter(prefix="/v1")

router.include_router(health.router)
router.include_router(users.router)
router.include_router(skills.router)
router.include_router(matches.router)
router.include_router(chat.router)
router.include_router(auth.router)