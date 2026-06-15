"""Тесты подсистемы логирования."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from app.logging.logging_config import LOG_FORMAT, setup_logging


def test_setup_logging_creates_console_and_file_handlers(tmp_path, monkeypatch):
    monkeypatch.setattr("app.logging.logging_config.settings.log_dir", str(tmp_path))
    monkeypatch.setattr("app.logging.logging_config.settings.log_file", "test.log")

    setup_logging()

    root = logging.getLogger()
    assert len(root.handlers) == 2

    handler_types = {type(h) for h in root.handlers}
    assert logging.StreamHandler in handler_types
    assert RotatingFileHandler in handler_types

    log_file = tmp_path / "test.log"
    logging.getLogger("app.test").info("test message")
    for handler in root.handlers:
        handler.flush()

    assert log_file.exists()
    content = log_file.read_text(encoding="utf-8")
    assert "test message" in content
    assert "] [INFO] [" in content


def test_log_format_matches_assignment_spec():
    assert "%(asctime)s" in LOG_FORMAT
    assert "%(levelname)s" in LOG_FORMAT
    assert "%(filename)s:%(lineno)d" in LOG_FORMAT
