from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.listing import ListingInterestStatus, ListingStatus


class ListingCreate(BaseModel):
    """Создание объявления об обмене навыками."""

    title: str = Field(
        description="Заголовок объявления", examples=["Урок Python за урок английского"]
    )
    description: str | None = Field(
        default=None,
        description="Подробное описание",
        examples=["Готов помочь с основами Python 2 раза в неделю."],
    )
    offering_summary: str = Field(description="Что предлагаю", examples=["Основы Python"])
    seeking_summary: str = Field(
        description="Что хочу получить", examples=["Разговорный английский"]
    )
    status: ListingStatus = Field(
        default=ListingStatus.published,
        description="Статус: draft, published, archived",
    )


class ListingUpdate(BaseModel):
    """Частичное обновление объявления (только автор)."""

    title: str | None = None
    description: str | None = None
    offering_summary: str | None = None
    seeking_summary: str | None = None
    status: ListingStatus | None = None


class ListingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_id: int
    author_full_name: str | None = None
    title: str
    description: str | None
    offering_summary: str
    seeking_summary: str
    status: ListingStatus
    created_at: datetime


class ListingInterestCreate(BaseModel):
    """Отклик на объявление."""

    message: str | None = Field(
        default=None,
        description="Сопроводительное сообщение автору",
        examples=["Интересен обмен, могу заниматься по вечерам."],
    )


class ListingInterestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    listing_id: int
    responder_id: int
    message: str | None
    status: ListingInterestStatus
    created_at: datetime


class ListingInterestDetailOut(ListingInterestOut):
    listing_title: str
    responder_full_name: str


def listing_to_out(listing: object, author_full_name: str | None) -> ListingOut:
    return ListingOut.model_validate(listing).model_copy(
        update={"author_full_name": author_full_name}
    )
