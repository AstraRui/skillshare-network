from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None

    @field_validator("password")
    @classmethod
    def validate_pass(cls, v: str) -> str:
        if len(v) < 10:
            raise ValueError("Пароль должен содержать минимум 10 символов")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str | None
    role: str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    #Bearer — это тип токена в стандарте OAuth2. 
    #Означает "предъявитель" — кто предъявил токен, тот и авторизован.
    token_type: str = "bearer" 