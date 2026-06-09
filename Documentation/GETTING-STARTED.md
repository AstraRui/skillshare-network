# Установка и локальный запуск

Пошаговое руководство для разработчиков: архитектура, структура репозитория, два способа запуска и настройка окружения.

## Архитектура системы

SkillShare Network — клиент-серверное SPA-приложение с REST API и in-process WebSocket-рассылкой сообщений.

```mermaid
flowchart LR
  subgraph client [Браузер]
    SPA[React SPA Vite]
  end
  subgraph server [Сервер приложений]
    Nginx[Nginx prod / Vite dev]
    API[FastAPI /api/v1]
    WS[WebSocket manager]
  end
  subgraph data [Данные]
    PG[(PostgreSQL)]
    RD[(Redis)]
  end
  SPA -->|HTTP /api| Nginx
  Nginx --> API
  SPA -->|WS broadcast| API
  API --> PG
  API --> RD
  WS --> RD
```

| Слой | Технология | Назначение |
| --- | --- | --- |
| Frontend | React 18, Vite, TailwindCSS | UI, маршрутизация, вызовы API |
| Backend | FastAPI, SQLAlchemy 2 async | Бизнес-логика, валидация (Pydantic) |
| БД | PostgreSQL 16 | Пользователи, объявления, сделки, чаты |
| Кэш / pub-sub | Redis 7 | Подготовка под кэш и масштабирование WS |
| Миграции | Alembic | Версионирование схемы БД |
| Auth | JWT (Bearer) | `Authorization: Bearer <token>` |
| Ops | Docker Compose, Gunicorn + Uvicorn workers | Dev и production |

Все HTTP-эндпоинты API — под префиксом `/api/v1/` (см. `backend/app/api/v1/router.py`).

## Структура репозитория

```
skillshare-network/
├── README.md                 # Краткое описание и ссылки
├── config/README.md          # Карта .gitignore, CI, dotfiles (сами файлы — в корне)
├── Makefile                  # lint, format, security из корня
├── docker-compose.yml        # Dev: postgres, redis, backend, frontend
├── docker-compose.prod.yml   # Production stack
├── .prod-secrets/            # Локальные секреты prod (создаётся вручную, в .gitignore)
│
├── backend/
│   ├── app/
│   │   ├── api/v1/           # REST: auth, users, listings, exchanges, chat, admin, …
│   │   ├── api/deps.py       # JWT-аутентификация
│   │   ├── core/settings.py  # Настройки из env (префикс SSN_)
│   │   ├── crud/             # Запросы к БД
│   │   ├── models/           # SQLAlchemy-модели
│   │   ├── schemas/          # Pydantic-схемы
│   │   ├── services/         # Доменная логика
│   │   ├── policies/         # Правила (чат, модерация)
│   │   ├── ws/               # WebSocket connection manager
│   │   └── main.py           # Точка входа FastAPI
│   ├── alembic/              # Миграции БД
│   ├── tests/
│   ├── .env.example
│   ├── Dockerfile            # builder (dev) + runtime (prod)
│   ├── entrypoint.sh         # Чтение Docker secrets в prod
│   └── gunicorn_conf.py
│
├── frontend/
│   ├── src/
│   │   ├── pages/            # Dashboard, Deals, Messages, Admin, …
│   │   ├── components/       # auth, deals, layout, listings, network, ui
│   │   ├── api/client.js     # HTTP-клиент к backend
│   │   └── context/          # AuthContext
│   ├── .env.example
│   ├── vite.config.js        # Прокси /api → backend
│   ├── nginx.conf            # Nginx внутри prod-образа frontend
│   └── Dockerfile / Dockerfile.dev
│
└── Documentation/            # Вся развёрнутая документация
```

## Требования

| Компонент | Версия |
| --- | --- |
| Python | 3.12+ |
| [uv](https://astral.sh/uv/) | последняя |
| Node.js | 20+ (LTS) |
| PostgreSQL | 16+ (локально или Docker) |
| Redis | 7+ (опционально для части функций; в compose включён) |
| Docker + Compose | v2 (для контейнерного запуска) |

---

## Вариант 1: Обычный запуск (без Docker)

### 1. База данных

Поднимите PostgreSQL и создайте БД `skillshare`, либо используйте только Docker для БД:

```bash
docker compose --profile infra up -d
```

### 2. Backend

```bash
cd backend
cp .env.example .env
# Отредактируйте SSN_DATABASE_URL при необходимости
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Проверка:

- Health: http://localhost:8000/api/v1/health
- Swagger: http://localhost:8000/docs

Опционально — сиды:

```bash
uv run python scripts/seed.py
```

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm ci
npm run dev
```

Откройте http://localhost:5173. Vite проксирует `/api` на `VITE_PROXY_TARGET` (по умолчанию `http://localhost:8000`).

### 4. Миграции при изменении моделей

```bash
cd backend
uv run alembic revision --autogenerate -m "описание"
uv run alembic upgrade head
```

---

## Вариант 2: Docker Compose

Файл `docker-compose.yml` поддерживает профили:

| Профиль | Сервисы | Команда |
| --- | --- | --- |
| `infra` | postgres, redis | `docker compose --profile infra up` |
| `backend` | infra + backend (hot-reload) | `docker compose --profile backend up --build` |
| `full` | infra + backend + frontend (Vite dev) | `docker compose --profile full up --build` |

**Полный стек для разработки:**

```bash
docker compose --profile full up --build
```

| Сервис | Порт | Примечание |
| --- | --- | --- |
| PostgreSQL | 5432 | user/pass/db: `postgres` / `postgres` / `skillshare` |
| Redis | 6379 | |
| Backend | 8000 | Alembic upgrade при старте, uvicorn `--reload` |
| Frontend | 5173 | `VITE_PROXY_TARGET=http://backend:8000` |

**Остановка:**

```bash
docker compose --profile full down
# с удалением тома БД:
docker compose --profile full down -v
```

Переменные для Docker backend задаются в `docker-compose.yml` (`SSN_DATABASE_URL`, `SSN_REDIS_URL`). Файл `backend/.env` подключается через `env_file`.

---

## Матрица переменных окружения

Полный справочник с примерами — [ENV.md](./ENV.md). Краткая таблица:

### Backend (`backend/.env`, префикс `SSN_`)

| Переменная | Обязательна | Пример (демо) | Назначение |
| --- | --- | --- | --- |
| `SSN_ENVIRONMENT` | нет | `local` | Режим: `local`, `docker`, `production` |
| `SSN_SECRET_KEY` | **да в prod** | `change-me-in-production` | Секрет для подписи JWT |
| `SSN_DATABASE_URL` | **да** | `postgresql+asyncpg://postgres:postgres@localhost:5432/skillshare` | Async URL PostgreSQL |
| `SSN_REDIS_URL` | нет | `redis://localhost:6379/0` | Redis |
| `SSN_PUBLIC_BASE_URL` | нет | `https://skillshare.example.com` | Публичный URL (ссылки, CORS при расширении) |

### Frontend (`frontend/.env`)

| Переменная | Обязательна | Пример (демо) | Назначение |
| --- | --- | --- | --- |
| `VITE_PROXY_TARGET` | нет (dev) | `http://localhost:8000` | Цель прокси Vite для `/api` |

### Docker Compose (dev, в `docker-compose.yml`)

| Переменная | Значение в compose |
| --- | --- |
| `POSTGRES_USER` / `PASSWORD` / `DB` | `postgres` / `postgres` / `skillshare` |
| `SSN_DATABASE_URL` (backend) | `postgresql+asyncpg://postgres:postgres@db:5432/skillshare` |
| `VITE_PROXY_TARGET` (frontend) | `http://backend:8000` |

---

## Следующие шаги

- API и Swagger: [API.md](./API.md)
- Production: [DEPLOYMENT.md](./DEPLOYMENT.md), [PRODUCTION-SECRETS.md](./PRODUCTION-SECRETS.md)
- Линтеры и CI: [DEVELOPMENT.md](./DEVELOPMENT.md)
