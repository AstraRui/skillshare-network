from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.skill import Skill, UserSkillsOffered, UserSkillsWanted
from app.models.user import User
from app.schemas.user import UserProfile, UserSkillsPayload, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me", response_model=UserProfile)
async def get_me(current_user: CurrentUser) -> User:
    """Возвращает профиль текущего авторизованного пользователя."""
    return current_user


@router.patch("/me", response_model=UserProfile)
async def update_me(
    payload: UserUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> User:
    """Обновляет имя и/или аватар текущего пользователя."""
    if payload.full_name is not None:
        current_user.full_name = payload.full_name.strip() or None
    if payload.avatar_url is not None:
        current_user.avatar_url = payload.avatar_url.strip() or None
    await db.flush()
    await db.refresh(current_user)
    return current_user


@router.put("/me/skills")
async def update_my_skills(
    payload: UserSkillsPayload,
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """
    Полностью заменяет навыки пользователя.
    offered: [{skill_id, level}]
    wanted:  [{skill_id, desired_level}]
    """
    # Проверяем что все skill_id существуют
    all_ids = {s.skill_id for s in payload.offered} | {s.skill_id for s in payload.wanted}
    if all_ids:
        existing = set(
            await db.scalars(
                select(Skill.id).where(Skill.id.in_(all_ids), Skill.is_deleted.is_(False))
            )
        )
        missing = all_ids - existing
        if missing:
            raise HTTPException(status_code=400, detail=f"Unknown skill ids: {sorted(missing)}")

    # Удаляем старые записи
    old_offered = list(
        await db.scalars(
            select(UserSkillsOffered).where(UserSkillsOffered.user_id == current_user.id)
        )
    )
    for row in old_offered:
        await db.delete(row)

    old_wanted = list(
        await db.scalars(
            select(UserSkillsWanted).where(UserSkillsWanted.user_id == current_user.id)
        )
    )
    for row in old_wanted:
        await db.delete(row)

    await db.flush()

    # Добавляем новые
    for s in payload.offered:
        db.add(UserSkillsOffered(user_id=current_user.id, skill_id=s.skill_id, level=s.level))
    for s in payload.wanted:
        db.add(
            UserSkillsWanted(
                user_id=current_user.id, skill_id=s.skill_id, desired_level=s.desired_level
            )
        )

    await db.flush()
    return {"ok": True}


@router.get("/me/skills")
async def get_my_skills(
    db: DbSession,
    current_user: CurrentUser,
) -> dict:
    """Возвращает текущие навыки пользователя."""
    offered = list(
        await db.scalars(
            select(UserSkillsOffered).where(UserSkillsOffered.user_id == current_user.id)
        )
    )
    wanted = list(
        await db.scalars(
            select(UserSkillsWanted).where(UserSkillsWanted.user_id == current_user.id)
        )
    )
    return {
        "offered": [{"skill_id": r.skill_id, "level": r.level} for r in offered],
        "wanted": [{"skill_id": r.skill_id, "desired_level": r.desired_level} for r in wanted],
    }
