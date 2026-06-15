from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Тело запроса регистрации."""

    email: EmailStr = Field(description="Email пользователя", examples=["user@example.com"])
    password: str = Field(
        description="Пароль (минимум 10 символов)",
        min_length=10,
        examples=["SecurePass123"],
    )
    full_name: str | None = Field(
        default=None,
        description="Отображаемое имя",
        examples=["Иван Иванов"],
    )

    @field_validator("password")
    @classmethod
    def validate_pass(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Пароль должен содержать минимум 10 символов")
        return v


class UserLogin(BaseModel):
    """Тело запроса входа."""

    email: str = Field(description="Email", examples=["user@example.com"])
    password: str = Field(description="Пароль", examples=["SecurePass123"])


class UserResponse(BaseModel):
    """Ответ после регистрации."""

    id: int = Field(description="ID пользователя", examples=[1])
    email: str = Field(examples=["user@example.com"])
    full_name: str | None = Field(examples=["Иван Иванов"])
    role: str = Field(description="Роль: user или admin", examples=["user"])

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT-токен для заголовка Authorization: Bearer ..."""

    access_token: str = Field(
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer", description="Тип токена (OAuth2 Bearer)", examples=["bearer"]
    )


class UserProfile(BaseModel):
    """Полный профиль текущего пользователя."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None
    avatar_url: str | None
    rating: float = Field(description="Средний рейтинг по отзывам", examples=[4.5])
    role: str


class UserUpdate(BaseModel):
    """Поля которые пользователь может изменить сам."""

    full_name: str | None = Field(default=None, examples=["Новое имя"])
    avatar_url: str | None = Field(default=None, examples=["https://cdn.example.com/avatar.png"])


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(description="Текущий пароль")
    new_password: str = Field(description="Новый пароль (минимум 10 символов)", min_length=10)

    @field_validator("new_password")
    @classmethod
    def validate_new_pass(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Пароль должен содержать минимум 10 символов")
        return v


class UserSkillOffered(BaseModel):
    skill_id: int = Field(description="ID навыка из справочника", examples=[1])
    level: int = Field(description="Уровень владения 1–3", ge=1, le=3, examples=[2])


class UserSkillWanted(BaseModel):
    skill_id: int = Field(description="ID желаемого навыка", examples=[2])
    desired_level: int = Field(description="Желаемый уровень 1–3", ge=1, le=3, examples=[1])


class UserSkillsPayload(BaseModel):
    """Полная замена навыков пользователя."""

    offered: list[UserSkillOffered] = Field(default_factory=list, description="Чему могу научить")
    wanted: list[UserSkillWanted] = Field(default_factory=list, description="Чему хочу научиться")
