import logging
import sys

# настройка логов при старте приложения
def setup_logging() -> None:
    # настройка вывода логов
    handler = logging.StreamHandler(sys.stdout)
    # в каком формате выводить логи
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)

    # применение настроек логирования
    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
        force=True,
    )

    # отключение системных логов
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False
