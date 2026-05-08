from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("skill_categories.id", ondelete="SET NULL"), index=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_moderated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    moderated_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    parent = relationship("SkillCategory", remote_side=[id])
    skills = relationship("Skill", back_populates="category")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    category_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skill_categories.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_moderated: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    moderated_by: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), index=True
    )

    category = relationship("SkillCategory", back_populates="skills")


class UserSkillsOffered(Base):
    __tablename__ = "user_skills_offered"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skills_offered"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    user = relationship("User", back_populates="offered_skills")
    skill = relationship("Skill")


class UserSkillsWanted(Base):
    __tablename__ = "user_skills_wanted"
    __table_args__ = (UniqueConstraint("user_id", "skill_id", name="uq_user_skills_wanted"),)

    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    skill_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True
    )
    desired_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    priority: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)

    user = relationship("User", back_populates="wanted_skills")
    skill = relationship("Skill")
