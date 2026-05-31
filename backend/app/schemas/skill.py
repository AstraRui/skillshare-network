from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SkillCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    parent_id: int | None


class SkillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category_id: int
    description: str | None


class SkillCreate(BaseModel):
    name: str
    category_id: int | None = None
