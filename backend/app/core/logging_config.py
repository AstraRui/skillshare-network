from __future__ import annotations

import json
import logging
import sys
import uuid
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        if hasattr(record, "path"):
            log_data["path"] = record.path

        if hasattr(record, "method"):
            log_data["method"] = record.method

        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code

        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )

    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False


def generate_request_id() -> str:
    return str(uuid.uuid4())
