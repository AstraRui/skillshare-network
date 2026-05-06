from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/users", tags=["users"])

# TODO: GET /users, POST /users, GET /users/{id}
