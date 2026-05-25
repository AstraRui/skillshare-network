import asyncio
import logging
import time
from uuid import uuid4

from fastapi import Request, Response

logger = logging.getLogger("app.requests")

SKIP_PATHS = {"/health", "/docs", "/openapi.json", "/favicon.ico"}


async def logging_middleware(request: Request, call_next):
    if request.url.path in SKIP_PATHS:
        return await call_next(request)

    request_id = str(uuid4())[:8]
    request.state.request_id = request_id

    start_time = time.perf_counter()

    client_ip = request.headers.get("x-forwarded-for", "")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    elif request.client:
        client_ip = request.client.host

    try:
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        logger.info(
            "[%s] %s %s -> %d (%.3fs) ip=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration,
            client_ip,
        )

        response.headers["X-Request-ID"] = request_id
        return response

    except (asyncio.CancelledError, ConnectionError):
        duration = time.perf_counter() - start_time
        logger.warning(
            "[%s] %s %s -> CANCELLED (%.3fs)",
            request_id,
            request.method,
            request.url.path,
            duration,
        )
        raise

    except Exception:
        duration = time.perf_counter() - start_time
        logger.exception(
            "[%s] %s %s -> ERROR (%.3fs) ip=%s",
            request_id,
            request.method,
            request.url.path,
            duration,
            client_ip,
        )
        raise
