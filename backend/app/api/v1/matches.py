from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/matches", tags=["matches"])

def get_matches(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # matches = find_matches(db, current_user.id)     
    return MatchResponse(matches=matches)
