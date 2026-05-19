from __future__ import annotations

from fastapi import HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def _validation_detail_message(err: dict) -> str:
    msg = err.get("msg", "Ошибка валидации")
    if isinstance(msg, str) and msg.startswith("Value error, "):
        return msg.removeprefix("Value error, ")
    return str(msg)


async def request_validation_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    messages = [_validation_detail_message(e) for e in exc.errors()]
    detail = ". ".join(dict.fromkeys(messages)) if messages else "Ошибка валидации"
    return JSONResponse(status_code=422, content={"detail": detail})


async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if not isinstance(detail, str):
        detail = str(detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


async def integrity_error_handler(_request: Request, exc: IntegrityError) -> JSONResponse:
    message = str(exc.orig) if exc.orig else str(exc)
    if "users_email" in message or "email" in message.lower():
        return JSONResponse(
            status_code=409,
            content={"detail": "Пользователь с таким email уже зарегистрирован"},
        )
    return JSONResponse(status_code=409, content={"detail": "Конфликт данных"})
