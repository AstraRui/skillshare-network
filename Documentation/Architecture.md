# Архитектура проекта

SkillShare Network разделён на **backend** (FastAPI) и **frontend** (React + Vite). Связь — REST API `/api/v1/*`, JWT в заголовке `Authorization`.

## Backend (FastAPI)

| Компонент | Роль |
| --- | --- |
| FastAPI | HTTP API, OpenAPI, middleware логирования |
| SQLAlchemy 2.0 (async) | ORM, PostgreSQL |
| Alembic | Миграции схемы |
| Pydantic v2 | Валидация запросов/ответов |
| Redis | Кэш и подготовка к pub/sub (WebSocket масштабирование) |
| Gunicorn + Uvicorn workers | Production WSGI/ASGI |

Слои в `backend/app/`:

- **api/v1** — маршруты по доменам
- **schemas** — контракты API
- **services / crud** — бизнес-логика и доступ к данным
- **models** — таблицы БД
- **policies** — правила чата и модерации
- **ws** — менеджер WebSocket-подключений по `chat_id`

## Frontend (React + Vite)

| Компонент | Роль |
| --- | --- |
| React 18 | UI, Context (auth), React Router |
| Vite | Dev-сервер, HMR, сборка |
| TailwindCSS | Стили |
| `src/api/client.js` | Единый HTTP-клиент |

Production: статика в Nginx, прокси `/api/` на backend.

## Поток данных: создание сделки

1. Пользователь A публикует объявление → `POST /api/v1/listings`
2. Пользователь B откликается → `POST /api/v1/listings/{id}/interests`
3. A принимает отклик → `POST /api/v1/exchanges/listing/{id}/accept-interest` → создаются Exchange и Chat
4. Переписка → `POST /api/v1/exchanges/{id}/messages` (+ WS broadcast участникам)
5. Завершение → `POST /api/v1/exchanges/{id}/confirm-completion`
6. Отзывы → `POST /api/v1/exchanges/{id}/reviews`

## Технологический стек

| Слой | Технологии |
| --- | --- |
| Backend | Python 3.12, FastAPI |
| ORM | SQLAlchemy 2.0 async, Alembic |
| БД | PostgreSQL 16+ |
| Кэш | Redis 7+ |
| Frontend | React 18, Vite |
| UI | TailwindCSS |
| Auth | JWT (Bearer) |
| Качество | Ruff, ESLint, Prettier, pip-audit, Bandit, npm audit |
| Контейнеры | Docker, Docker Compose |
| CI | GitHub Actions |

## Планируемые расширения

| Фича | Статус |
| --- | --- |
| WebSocket чат (in-process) | Реализовано (`app/ws/manager.py`) |
| Redis pub/sub для WS | Планируется |
| Рекурсивные CTE / chain matching | Планируется |

Подробнее о запуске: [GETTING-STARTED.md](./GETTING-STARTED.md).
