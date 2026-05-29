from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.models.skill import Skill, SkillCategory
from app.schemas.skill import SkillCategoryOut, SkillCreate, SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


@router.get("/categories", response_model=list[SkillCategoryOut])
async def get_categories(db: DbSession) -> list[SkillCategory]:
    result = await db.scalars(
        select(SkillCategory)
        .where(SkillCategory.is_deleted.is_(False))
        .order_by(SkillCategory.name)
    )
    return list(result)


@router.get("", response_model=list[SkillOut])
async def get_skills(db: DbSession, category_id: int | None = None) -> list[Skill]:
    """Список навыков, опционально фильтр по категории."""
    stmt = select(Skill).where(Skill.is_deleted.is_(False))
    if category_id is not None:
        stmt = stmt.where(Skill.category_id == category_id)
    stmt = stmt.order_by(Skill.name)
    return list(await db.scalars(stmt))


@router.post("", response_model=SkillOut, status_code=201)
async def create_skill(payload: SkillCreate, db: DbSession) -> Skill:
    """Создать новый навык. Если категории нет — создаём дефолтную."""
    # Проверяем есть ли уже такой навык
    existing = await db.scalar(
        select(Skill).where(Skill.name == payload.name.strip(), Skill.is_deleted.is_(False))
    )
    if existing:
        return existing

    # Если категории нет — создаём "Общее"
    if not payload.category_id:
        default_cat = await db.scalar(select(SkillCategory).where(SkillCategory.name == "Общее"))
        if not default_cat:
            default_cat = SkillCategory(name="Общее")
            db.add(default_cat)
            await db.flush()
            await db.refresh(default_cat)
        category_id = default_cat.id
    else:
        category_id = payload.category_id

    skill = Skill(name=payload.name.strip(), category_id=category_id)
    db.add(skill)
    await db.flush()
    await db.refresh(skill)
    return skill
