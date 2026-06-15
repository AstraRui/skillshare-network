from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Awaitable, Callable
from urllib.parse import parse_qsl, urlencode
from uuid import uuid4

from fastapi import Request, Response

logger = logging.getLogger("app.requests")

NOISY_PATHS = {
    "/health",
    "/api/v1/health",
    "/metrics",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}

SENSITIVE_KEYS = {
    "token",
    "access_token",
    "refresh_token",
    "password",
    "secret",
    "api_key",
    "authorization",
}


def _mask_query_params(query_string: str) -> str:
    if not query_string:
        return ""

    masked_params = []

    for key, value in parse_qsl(query_string, keep_blank_values=True):
        if key.lower() in SENSITIVE_KEYS:
            masked_params.append((key, "***"))
        else:
            masked_params.append((key, value))

    return urlencode(masked_params)


def _get_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        return forwarded_for.split(",")[0].strip()

    if request.client:
        return request.client.host

    return None


def _get_log_level(status_code: int) -> int:
    if status_code >= 500:
        return logging.ERROR

    if status_code >= 400:
        return logging.WARNING

    return logging.INFO


async def logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.url.path in NOISY_PATHS:
        return await call_next(request)

    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id

    start_time = time.perf_counter()

    method = request.method
    path = request.url.path
    query_params = _mask_query_params(request.url.query)
    client_ip = _get_client_ip(request)
    user_agent = request.headers.get("user-agent")

    try:
        response = await call_next(request)

    except (asyncio.CancelledError, ConnectionError):
        duration = time.perf_counter() - start_time

        logger.warning(
            "Request cancelled or disconnected",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": 499,
                "duration": round(duration, 4),
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        raise

    except Exception:
        duration = time.perf_counter() - start_time

        logger.exception(
            "Unhandled server error",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query_params": query_params,
                "status_code": 500,
                "duration": round(duration, 4),
                "client_ip": client_ip,
                "user_agent": user_agent,
            },
        )

        raise

    duration = time.perf_counter() - start_time
    status_code = response.status_code

    response.headers["X-Request-ID"] = request_id

    logger.log(
        _get_log_level(status_code),
        "HTTP request completed",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "query_params": query_params,
            "status_code": status_code,
            "duration": round(duration, 4),
            "client_ip": client_ip,
            "user_agent": user_agent,
        },
    )

    return response
