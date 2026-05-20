from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserSkillOut(BaseModel):
    skill_id: int
    name: str
    level: int | None = None
    desired_level: int | None = None


class UserSkillsOut(BaseModel):
    offered: list[UserSkillOut]
    wanted: list[UserSkillOut]


class MyProfileOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None
    rating: float
    exchanges_count: int
    listings_count: int


class UserProfileUpdate(BaseModel):
    full_name: str | None = None

    @field_validator("full_name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class UserSkillAdd(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    level: int = Field(default=2, ge=1, le=3)
    desired_level: int = Field(default=2, ge=1, le=3)

    @field_validator("name")
    @classmethod
    def normalize_skill_name(cls, value: str) -> str:
        return value.strip()
