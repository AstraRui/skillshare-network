from __future__ import annotations
from pydantic import BaseModel, ConfigDict

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str | None = None

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