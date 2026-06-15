from __future__ import annotations

import copy
import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.core.settings import settings

# [Дата и время] [Уровень] [Имя файла:Строка] - Сообщение
LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_REQUEST_EXTRA_FIELDS = (
    "request_id",
    "method",
    "path",
    "query_params",
    "status_code",
    "duration",
    "client_ip",
    "user_agent",
)


class AppTextFormatter(logging.Formatter):
    """Текстовый формат для консоли (Docker stdout) и файла с ротацией."""

    def format(self, record: logging.LogRecord) -> str:
        extras = [
            f"{field}={getattr(record, field)}"
            for field in _REQUEST_EXTRA_FIELDS
            if hasattr(record, field)
        ]
        if extras:
            record = copy.copy(record)
            record.msg = f"{record.getMessage()} | {' | '.join(extras)}"
            record.args = ()

        formatted = super().format(record)

        if record.exc_info:
            formatted = f"{formatted}\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logging() -> logging.Logger:
    """Настраивает console + file handlers с ротацией. Вызывается при старте приложения."""
    log_dir = Path(settings.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / settings.log_file

    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    formatter = AppTextFormatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=settings.log_max_bytes,
        backupCount=settings.log_backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    # Дублирование access-логов uvicorn отключаем — HTTP пишет logging_middleware
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False

    app_logger = logging.getLogger("app")
    app_logger.info(
        "Logging initialized: console=stdout file=%s max_bytes=%d backups=%d",
        log_path,
        settings.log_max_bytes,
        settings.log_backup_count,
    )
    return app_logger
