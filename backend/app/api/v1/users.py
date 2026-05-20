from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db_session
from app.models.exchange import Exchange
from app.models.listing import Listing, ListingInterest, ListingInterestStatus
from app.models.skill import UserSkillsOffered, UserSkillsWanted
from app.models.user import User
from app.schemas.profile import (
    MyProfileOut,
    UserProfileUpdate,
    UserSkillAdd,
    UserSkillOut,
    UserSkillsOut,
)
from app.services.user_skills import get_or_create_skill, load_user_skills

router = APIRouter(prefix="/users", tags=["users"])


class PublicUserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str | None
    email: str | None = None


DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def _count_exchanges(db: AsyncSession, user_id: int) -> int:
    count = await db.scalar(
        select(func.count(Exchange.id)).where(
            or_(
                Exchange.initiator_id == user_id,
                Exchange.listing_id.in_(
                    select(ListingInterest.listing_id).where(
                        ListingInterest.responder_id == user_id,
                        ListingInterest.status == ListingInterestStatus.accepted,
                    )
                ),
            )
        )
    )
    return int(count or 0)


async def _count_listings(db: AsyncSession, user_id: int) -> int:
    count = await db.scalar(select(func.count(Listing.id)).where(Listing.author_id == user_id))
    return int(count or 0)


def _profile_out(user: User, exchanges_count: int, listings_count: int) -> MyProfileOut:
    return MyProfileOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        rating=float(user.rating),
        exchanges_count=exchanges_count,
        listings_count=listings_count,
    )


@router.get("/me", response_model=MyProfileOut)
async def get_my_profile(db: DbSession, current_user: CurrentUser) -> MyProfileOut:
    exchanges_count = await _count_exchanges(db, current_user.id)
    listings_count = await _count_listings(db, current_user.id)
    return _profile_out(current_user, exchanges_count, listings_count)


@router.patch("/me", response_model=MyProfileOut)
async def update_my_profile(
    payload: UserProfileUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> MyProfileOut:
    if payload.full_name is not None:
        current_user.full_name = payload.full_name

    exchanges_count = await _count_exchanges(db, current_user.id)
    listings_count = await _count_listings(db, current_user.id)
    return _profile_out(current_user, exchanges_count, listings_count)


@router.get("/me/skills", response_model=UserSkillsOut)
async def get_my_skills(db: DbSession, current_user: CurrentUser) -> UserSkillsOut:
    offered_rows, wanted_rows = await load_user_skills(db, current_user.id)
    return UserSkillsOut(
        offered=[
            UserSkillOut(skill_id=skill_id, name=name, level=level)
            for skill_id, name, level in offered_rows
        ],
        wanted=[
            UserSkillOut(skill_id=skill_id, name=name, desired_level=level)
            for skill_id, name, level in wanted_rows
        ],
    )


@router.post("/me/skills/offered", response_model=UserSkillOut, status_code=201)
async def add_offered_skill(
    payload: UserSkillAdd,
    db: DbSession,
    current_user: CurrentUser,
) -> UserSkillOut:
    skill = await get_or_create_skill(db, payload.name)
    existing = await db.get(UserSkillsOffered, (current_user.id, skill.id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Этот навык уже в списке «Я предлагаю»")

    db.add(
        UserSkillsOffered(
            user_id=current_user.id,
            skill_id=skill.id,
            level=payload.level,
        )
    )
    await db.flush()
    return UserSkillOut(skill_id=skill.id, name=skill.name, level=payload.level)


@router.post("/me/skills/wanted", response_model=UserSkillOut, status_code=201)
async def add_wanted_skill(
    payload: UserSkillAdd,
    db: DbSession,
    current_user: CurrentUser,
) -> UserSkillOut:
    skill = await get_or_create_skill(db, payload.name)
    existing = await db.get(UserSkillsWanted, (current_user.id, skill.id))
    if existing is not None:
        raise HTTPException(status_code=409, detail="Этот навык уже в списке «Я ищу»")

    db.add(
        UserSkillsWanted(
            user_id=current_user.id,
            skill_id=skill.id,
            desired_level=payload.desired_level,
        )
    )
    await db.flush()
    return UserSkillOut(skill_id=skill.id, name=skill.name, desired_level=payload.desired_level)


@router.delete("/me/skills/offered/{skill_id}", status_code=204)
async def remove_offered_skill(
    skill_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    row = await db.get(UserSkillsOffered, (current_user.id, skill_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Навык не найден")
    await db.delete(row)


@router.delete("/me/skills/wanted/{skill_id}", status_code=204)
async def remove_wanted_skill(
    skill_id: int,
    db: DbSession,
    current_user: CurrentUser,
) -> None:
    row = await db.get(UserSkillsWanted, (current_user.id, skill_id))
    if row is None:
        raise HTTPException(status_code=404, detail="Навык не найден")
    await db.delete(row)


@router.get("/{user_id}", response_model=PublicUserOut)
async def get_user(user_id: int, db: DbSession) -> PublicUserOut:
    user = await db.get(User, user_id)
    if user is None or user.is_deleted:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return PublicUserOut(id=user.id, full_name=user.full_name, email=None)
