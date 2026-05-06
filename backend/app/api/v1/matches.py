from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/matches", tags=["matches"])

# TODO: POST /matches/search — алгоритм поиска цепочек бартера
