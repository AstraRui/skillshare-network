from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.crud.match import find_matches
from app.models.user import User
from app.schemas.match import MatchResponse

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=MatchResponse)
async def get_matches(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> MatchResponse:
    matches = await find_matches(db, current_user.id, limit=limit, offset=offset)
    return MatchResponse(results=matches, total=len(matches))
