from __future__ import annotations

from fastapi import APIRouter, Depends
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
) -> MatchResponse:
    matches = await find_matches(db, current_user.id)
    return MatchResponse(results=matches, total=len(matches))