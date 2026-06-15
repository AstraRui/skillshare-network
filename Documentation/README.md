# Документация SkillShare Network

Центральный каталог технической документации проекта. Корневой [README.md](../README.md) содержит только краткое описание и ссылки сюда.

## Навигация

| Документ | Для кого | Содержание |
| --- | --- | --- |
| [Documentation.md](./Documentation.md) | Все | Описание продукта и функций |
| [GETTING-STARTED.md](./GETTING-STARTED.md) | Разработчик | Архитектура, дерево папок, локальный запуск (venv / Docker), матрица `.env` |
| [ENV.md](./ENV.md) | Разработчик, DevOps | Полный перечень переменных окружения с маскированными примерами |
| [API.md](./API.md) | Разработчик, интегратор | REST API, Swagger/OpenAPI, коды ошибок, Postman |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Администратор | Требования к серверу, Nginx, production Docker, регламент при сбоях |
| [PRODUCTION-SECRETS.md](./PRODUCTION-SECRETS.md) | Администратор | Файлы секретов для production Compose (не в git) |
| [Architecture.md](./Architecture.md) | Разработчик | Слои системы, потоки данных, стек |
| [DEVELOPMENT.md](./DEVELOPMENT.md) | Разработчик | Ruff, ESLint, pre-commit, CI |
| [LOGGING.md](./LOGGING.md) | DevOps, разработчик | Логирование, ротация, тест сбоев БД |
| [BACKUP.md](./BACKUP.md) | Администратор | Скрипты backup/restore PostgreSQL и uploads |

## Интерактивная API-документация

После запуска бэкенда:

| Ресурс | URL |
| --- | --- |
| Swagger UI (тест запросов из браузера) | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI 3.x (JSON) | http://localhost:8000/openapi.json |

Импорт в Postman: **Import → Link** → `http://localhost:8000/openapi.json`. Подробнее — [API.md](./API.md).

## Быстрые команды

```bash
# Локально: backend + frontend
cd backend && uv sync && cp .env.example .env && uv run uvicorn app.main:app --reload
cd frontend && npm ci && npm run dev

# Docker: postgres + redis + backend + frontend
docker compose --profile full up --build

# Production
# См. PRODUCTION-SECRETS.md и DEPLOYMENT.md
docker compose -f docker-compose.prod.yml up -d
```

## Качество кода

```bash
make install-tools   # один раз
make lint            # как в CI
make security        # аудит зависимостей
```

Подробности: [DEVELOPMENT.md](./DEVELOPMENT.md).
