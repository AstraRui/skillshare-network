"""Общие описания HTTP-ответов для OpenAPI / Swagger UI."""

from __future__ import annotations

from typing import Any

_JSON = "application/json"


def _error(description: str, example: str) -> dict[str, Any]:
    return {
        "description": description,
        "content": {_JSON: {"example": {"detail": example}}},
    }


RESP_400 = _error("Некорректный запрос (400 Bad Request)", "Неверный текущий пароль")
RESP_401 = _error(
    "Не авторизован (401 Unauthorized)",
    "Missing or invalid Authorization header",
)
RESP_403 = _error("Доступ запрещён (403 Forbidden)", "Only exchange members have access")
RESP_404 = _error("Ресурс не найден (404 Not Found)", "Объявление не найдено")
RESP_409 = _error(
    "Конфликт данных (409 Conflict)",
    "Пользователь с таким email уже зарегистрирован",
)
RESP_422 = _error(
    "Ошибка валидации (422 Unprocessable Entity)",
    "Пароль должен содержать минимум 10 символов",
)

# Публичные эндпоинты (без JWT)
PUBLIC_ERRORS: dict[int, dict[str, Any]] = {
    400: RESP_400,
    422: RESP_422,
}

# Эндпоинты с Bearer JWT
AUTH_ERRORS: dict[int, dict[str, Any]] = {
    **PUBLIC_ERRORS,
    401: RESP_401,
}

AUTH_ERRORS_404: dict[int, dict[str, Any]] = {
    **AUTH_ERRORS,
    404: RESP_404,
}

AUTH_ERRORS_FULL: dict[int, dict[str, Any]] = {
    **AUTH_ERRORS_404,
    403: RESP_403,
    409: RESP_409,
}

ADMIN_ERRORS: dict[int, dict[str, Any]] = {
    **AUTH_ERRORS_404,
    403: _error("Требуется роль admin (403 Forbidden)", "Admin access required"),
}
