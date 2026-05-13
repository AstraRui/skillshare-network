from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response

logger = logging.getLogger("app.requests")


async def logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

    except Exception:
        process_time = time.perf_counter() - start_time

        logger.exception(
            "Unhandled error | method=%s path=%s duration=%.3fs",
            request.method,
            request.url.path,
            process_time,
        )

        raise

    process_time = time.perf_counter() - start_time

    logger.info(
        "HTTP request | method=%s path=%s status=%s duration=%.3fs",
        request.method,
        request.url.path,
        response.status_code,
        process_time,
    )

    return response
