from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.openapi_responses import ADMIN_ERRORS
from app.db.session import get_db_session
from app.models.exchange import ExchangeStatus
from app.models.user import User
from app.policies.admin import get_current_admin
from app.schemas.admin import (
    AdminChatOut,
    AdminExchangeOut,
    AdminListingOut,
    AdminMessageOut,
    AdminReportOut,
    AdminUserOut,
    ExchangeStatusPatch,
    ListingStatusPatch,
    UserStatusPatch,
)
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"], responses=ADMIN_ERRORS)

DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CurrentAdmin = Annotated[User, Depends(get_current_admin)]


@router.get(
    "/users",
    response_model=list[AdminUserOut],
    summary="Список пользователей",
    description="Модерация: все пользователи с пагинацией. Требуется роль admin.",
)
async def get_admin_users(
    db: DbSession,
    admin: CurrentAdmin,
    # пагинация, лимит выданных пользователей на одной странице = 20, пропускать по умолчанию 0, ge = больше либо равно, le = меньше либо равно
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[AdminUserOut]:
    return await admin_service.get_users(db=db, admin=admin, limit=limit, offset=offset)


@router.get(
    "/users/{user_id}",
    response_model=AdminUserOut,
    summary="Пользователь по ID",
    description="Карточка пользователя. Не найден — 404.",
)
async def get_admin_user(
    user_id: int,
    db: DbSession,
    admin: CurrentAdmin,
) -> AdminUserOut:
    return await admin_service.get_user(db=db, admin=admin, user_id=user_id)


@router.patch(
    "/users/{user_id}/status",
    response_model=AdminUserOut,
    summary="Изменить статус пользователя",
    description="Блокировка, разблокировка, пометка fraudulent.",
)
async def patch_admin_user_status(
    user_id: int,
    payload: UserStatusPatch,
    db: DbSession,
    admin: CurrentAdmin,
) -> AdminUserOut:
    return await admin_service.update_user_status(
        db=db, admin=admin, user_id=user_id, payload=payload
    )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Заблокировать пользователя",
    description="Мягкая блокировка (is_deleted). Успех — 204 No Content.",
)
async def block_admin_user(
    user_id: int,
    db: DbSession,
    admin: CurrentAdmin,
) -> None:
    await admin_service.update_user_status(
        db=db, admin=admin, user_id=user_id, payload=UserStatusPatch(is_deleted=True)
    )


@router.get(
    "/listings",
    response_model=list[AdminListingOut],
    summary="Список объявлений",
    description="Все объявления для модерации.",
)
async def get_admin_listings(
    db: DbSession,
    admin: CurrentAdmin,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[AdminListingOut]:
    return await admin_service.get_listings(db=db, admin=admin, limit=limit, offset=offset)


@router.patch(
    "/listings/{listing_id}/status",
    response_model=AdminListingOut,
    summary="Статус объявления",
    description="Скрытие, публикация, архивация объявления.",
)
async def patch_admin_listing_status(
    listing_id: int,
    payload: ListingStatusPatch,
    db: DbSession,
    admin: CurrentAdmin,
) -> AdminListingOut:
    return await admin_service.update_listing_status(
        db=db, admin=admin, listing_id=listing_id, payload=payload
    )


@router.delete(
    "/listings/{listing_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить объявление",
    description="Мягкое удаление объявления. Успех — 204.",
)
async def delete_admin_listing(
    listing_id: int,
    db: DbSession,
    admin: CurrentAdmin,
) -> None:
    await admin_service.remove_listing(db=db, admin=admin, listing_id=listing_id)


@router.get(
    "/exchanges",
    response_model=list[AdminExchangeOut],
    summary="Список сделок",
    description="Все обмены с опциональным фильтром по статусу.",
)
async def get_admin_exchanges(
    db: DbSession,
    admin: CurrentAdmin,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    status: ExchangeStatus | None = Query(default=None),
) -> list[AdminExchangeOut]:
    return await admin_service.get_exchanges(
        db=db, admin=admin, limit=limit, offset=offset, status_filter=status
    )


@router.patch(
    "/exchanges/{exchange_id}/status",
    response_model=AdminExchangeOut,
    summary="Статус сделки",
    description="Принудительная смена статуса обмена модератором.",
)
async def patch_admin_exchange_status(
    exchange_id: int,
    payload: ExchangeStatusPatch,
    db: DbSession,
    admin: CurrentAdmin,
) -> AdminExchangeOut:
    return await admin_service.update_exchange_status(
        db=db, admin=admin, exchange_id=exchange_id, payload=payload
    )


@router.delete(
    "/exchanges/{exchange_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отменить сделку",
    description="Отмена обмена администратором. Успех — 204.",
)
async def delete_admin_exchange(
    exchange_id: int,
    db: DbSession,
    admin: CurrentAdmin,
) -> None:
    await admin_service.cancel_exchange(db=db, admin=admin, exchange_id=exchange_id)


@router.get(
    "/chats",
    response_model=list[AdminChatOut],
    summary="Список чатов",
    description="Все чаты сделок для модерации.",
)
async def get_admin_chats(
    db: DbSession,
    admin: CurrentAdmin,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[AdminChatOut]:
    return await admin_service.get_chats(db=db, admin=admin, limit=limit, offset=offset)


@router.get(
    "/chats/{chat_id}/messages",
    response_model=list[AdminMessageOut],
    summary="Сообщения чата",
    description="История сообщений чата для просмотра модератором.",
)
async def get_admin_chat_messages(
    chat_id: int,
    db: DbSession,
    admin: CurrentAdmin,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[AdminMessageOut]:
    return await admin_service.get_chat_messages(
        db=db, admin=admin, chat_id=chat_id, limit=limit, offset=offset
    )


@router.delete(
    "/chats/{chat_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Закрыть чат",
    description="Закрытие чата модератором. Успех — 204.",
)
async def delete_admin_chat(
    chat_id: int,
    db: DbSession,
    admin: CurrentAdmin,
) -> None:
    await admin_service.close_chat(db=db, admin=admin, chat_id=chat_id)


@router.get(
    "/reports",
    response_model=list[AdminReportOut],
    summary="Жалобы (заглушка)",
    description="Endpoint-заглушка для будущих жалоб. Возвращает пустой список.",
)
async def get_admin_reports(admin: CurrentAdmin) -> list[AdminReportOut]:
    # В проекте пока нет модели complaints/reports.
    # Endpoint оставлен как безопасный skeleton для будущего расширения.
    return []
