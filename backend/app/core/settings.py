from __future__ import annotations

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SSN_", extra="ignore")

    app_name: str = "SkillShare Network"
    environment: str = "local"
    #"change-me" — дефолтное значение только для разработки. 
    #В продакшене обязательно меняется на длинную случайную строку
    secret_key: str = "change-me" 

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/skillshare"
    redis_url: str = "redis://localhost:6379/0"

    #AnyUrl — специальный тип Pydantic, 
    #который проверяет что строка является валидным URL 
    #(есть протокол, домен и т.д.). 
    public_base_url: AnyUrl | None = None #Нужно когда надо генерировать абсолютные ссылки, например в письмахНужно когда надо генерировать абсолютные ссылки, например в письмах


settings = Settings()
