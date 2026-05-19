from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill, SkillCategory, UserSkillsOffered, UserSkillsWanted


async def get_default_category_id(db: AsyncSession) -> int:
    category_id = await db.scalar(
        select(SkillCategory.id).where(
            SkillCategory.name == "Общее",
            SkillCategory.is_deleted.is_(False),
        )
    )
    if category_id is not None:
        return category_id

    category = SkillCategory(name="Общее")
    db.add(category)
    await db.flush()
    return category.id


async def get_or_create_skill(db: AsyncSession, name: str) -> Skill:
    normalized = name.strip()
    skill = await db.scalar(
        select(Skill).where(
            func.lower(Skill.name) == normalized.lower(),
            Skill.is_deleted.is_(False),
        )
    )
    if skill is not None:
        return skill

    category_id = await get_default_category_id(db)
    skill = Skill(name=normalized, category_id=category_id)
    db.add(skill)
    await db.flush()
    return skill


async def load_user_skills(db: AsyncSession, user_id: int) -> tuple[list[tuple[int, str, int]], list[tuple[int, str, int]]]:
    offered_rows = (
        await db.execute(
            select(Skill.id, Skill.name, UserSkillsOffered.level)
            .join(UserSkillsOffered, UserSkillsOffered.skill_id == Skill.id)
            .where(UserSkillsOffered.user_id == user_id, Skill.is_deleted.is_(False))
            .order_by(Skill.name)
        )
    ).all()

    wanted_rows = (
        await db.execute(
            select(Skill.id, Skill.name, UserSkillsWanted.desired_level)
            .join(UserSkillsWanted, UserSkillsWanted.skill_id == Skill.id)
            .where(UserSkillsWanted.user_id == user_id, Skill.is_deleted.is_(False))
            .order_by(Skill.name)
        )
    ).all()

    return list(offered_rows), list(wanted_rows)
