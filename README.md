# SkillShare Network

Платформа взаимного обмена навыками: объявления, отклики, сделки, встроенный чат, отзывы и матчмейкинг.

## Быстрый старт

| Способ | Команда | URL |
| --- | --- | --- |
| Backend (локально) | `cd backend && uv sync && uv run uvicorn app.main:app --reload` | http://localhost:8000/docs |
| Frontend (локально) | `cd frontend && npm ci && npm run dev` | http://localhost:5173 |
| Docker (полный стек) | `docker compose --profile full up --build` | http://localhost:5173 |

Перед первым запуском: скопируйте `backend/.env.example` → `backend/.env`, поднимите PostgreSQL (или используйте Docker).

## Документация

Вся подробная информация — в каталоге **[Documentation/](./Documentation/)**:

| Документ | Содержание |
| --- | --- |
| [Documentation/README.md](./Documentation/README.md) | Навигация по документации |
| [Documentation/GETTING-STARTED.md](./Documentation/GETTING-STARTED.md) | Архитектура, структура репозитория, локальный запуск, матрица `.env` |
| [Documentation/DEPLOYMENT.md](./Documentation/DEPLOYMENT.md) | Production: сервер, Nginx, восстановление после сбоев |
| [Documentation/ENV.md](./Documentation/ENV.md) | Переменные окружения (с демо-значениями) |
| [Documentation/PRODUCTION-SECRETS.md](./Documentation/PRODUCTION-SECRETS.md) | Секреты для `docker-compose.prod.yml` |
| [Documentation/API.md](./Documentation/API.md) | REST API, Swagger, аутентификация |
| [Documentation/DEVELOPMENT.md](./Documentation/DEVELOPMENT.md) | Линтеры, CI, качество кода |
| [Documentation/LOGGING.md](./Documentation/LOGGING.md) | Логирование, ротация, мониторинг БД и auth |

**Интерактивная API-документация:** после запуска бэкенда — [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI), [http://localhost:8000/redoc](http://localhost:8000/redoc) (ReDoc), OpenAPI JSON — [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json).

## Стек (кратко)

Python 3.12 · FastAPI · PostgreSQL 16 · Redis 7 · React · Vite · Docker · GitHub Actions
