## SkillShare Network

Платформа для обмена навыками, где пользователи публикуют свои предложения (что они умеют и чему могут обучить) и указывают, что хотят получить взамен. Другие пользователи могут откликаться на эти предложения, и при взаимном интересе система создаёт сделку между двумя людьми.

Каждая сделка проходит через статусы: обсуждение, активный обмен и завершение. После создания сделки автоматически открывается чат внутри неё, через который участники договариваются и ведут сам обмен. В активной сделке переписка доступна только между участниками этой сделки, и она существует только в рамках её жизненного цикла.

После завершения сделки оба пользователя подтверждают результат и оценивают друг друга, формируя рейтинг доверия.

Отдельно есть вкладка “чаты”: там отображаются все текущие и завершённые сделки. Однако писать можно только в активных сделках — завершённые чаты остаются в виде архива истории и доступны только для просмотра, без возможности продолжить переписку.

Дополнительно система использует матчмейкинг, который анализирует навыки, запросы и историю обменов, чтобы предлагать наиболее подходящих людей для потенциального обмена с высокой вероятностью совпадения интересов.

## Технологический стек

| Слой | Технология | Почему |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | Максимальная скорость, асинхронность, мощная типизация (Pydantic) |
| Backend lint / format | Ruff | Заменяет Flake8, Black и Isort |
| Backend security | pip-audit + Bandit | Уязвимости в пакетах и базовый SAST |
| Frontend lint / format | ESLint + Prettier | Проверка React-кода и единый стиль |
| Frontend security | npm audit | Уязвимости в npm-зависимостях |
| Frontend | React + Vite | Современный компонентный подход, быстрая разработка |
| UI-компоненты | TailwindCSS | Профессиональный UI с минимальными стилями |
| ORM | SQLAlchemy 2.0 + Alembic | Работа со сложным SQL и рекурсиями для матчинга цепочек |
| База данных | PostgreSQL 16+ | Реляционная классика, идеальна для графовых запросов (CTE) |
| Real-time | WebSockets | Real-time чат через `/api/v1/chat/{id}/ws` |
| Auth | JWT + X-User-Id header | MVP-аутентификация через заголовки (см. `app/api/deps.py`) |
| Ops | Docker + GitHub Actions | Стандарт индустрии для контейнеризации и автоматизации |

## Архитектурный план (следующий спринт)

Каркас бэкенда подготовлен для расширения:

| Фича | Статус | Файл |
| --- | --- | --- |
| WebSocket чат | ✅ Работает | `app/ws/manager.py`, `app/api/v1/chat.py` |
| Правила переписки | ✅ Готов | `app/policies/exchange_messaging.py` |
| Redis кэш | 🔄 Планируется | - |
| Рекурсивные CTE для графов | 🔄 Планируется | SQLAlchemy 2.0 поддерживает CTE |
| Chain matching | 🔄 Планируется | Поиск цепочек обмена A→B→C |

## Структура репозитория

- `backend/`: FastAPI-приложение, DB слой и миграции Alembic
  - `backend/app/api/v1/`: HTTP API (единая точка `/api/v1/...`)
  - `backend/app/models|schemas|services|crud/`: слои приложения
- `frontend/`: SPA на React (Vite + TailwindCSS)
  - `frontend/src/pages/`: экраны (в т.ч. админка `/admin`)
  - `frontend/src/components/`: UI по доменам (auth, deals, layout, …)
  - `frontend/src/api/`: HTTP-клиент к API
- `Documentation/`: описание, архитектура, [инструкции для разработчиков](./Documentation/DEVELOPMENT.md)
- `secrets/`: локальные файлы для Docker prod (не в git)
- `docker-compose.yml`: PostgreSQL + backend

Подробнее о качестве кода и CI: [Documentation/DEVELOPMENT.md](./Documentation/DEVELOPMENT.md).

## Быстрый старт (локально)

Требования: Python 3.12+, [`uv`](https://astral.sh/uv/)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Открыть:
- `http://localhost:8000/docs` (Swagger UI; `/` редиректит сюда)
- `http://localhost:8000/api/v1/health` (healthcheck)

Фронтенд отдельно: `cd frontend && npm ci && npm run dev` → `http://localhost:5173`

### Качество кода и безопасность

Установка инструментов (один раз):

```bash
make install-tools
```

Проверка стиля (как на CI):

```bash
make lint
```

Автоформатирование:

```bash
make format
```

Исправление lint с автофиксом:

```bash
make lint-fix
```

Проверка уязвимостей в зависимостях и базовый SAST:

```bash
make security
# то же: make audit-deps
```

| Слой | Линтер / формат | Безопасность зависимостей | SAST |
| --- | --- | --- | --- |
| Backend | [Ruff](https://docs.astral.sh/ruff/) check + format | [pip-audit](https://pypi.org/project/pip-audit/) | [Bandit](https://bandit.readthedocs.io/) |
| Frontend | [ESLint](https://eslint.org/) + [Prettier](https://prettier.io/) | `npm audit` (`npm run audit`) | — |

В CI (`.github/workflows/ci.yml`) отдельные job'ы: lint, security, tests, docker-build.

Отдельно по каталогам:

```bash
# Backend
cd backend
uv run ruff check .
uv run ruff format .

# Frontend
cd frontend
npm run lint
npm run format:check   # только проверка
npm run format         # записать исправления
```

Опционально — хуки перед коммитом ([pre-commit](https://pre-commit.com/)):

```bash
pip install pre-commit   # или: uv tool install pre-commit
pre-commit install
pre-commit run --all-files
```

## Запуск через Docker

### Полный стек (backend + frontend + postgres)

```bash
docker compose --profile full up --build
```

### Только backend + postgres (без frontend)

```bash
docker compose up --build
```

### Остановка

```bash
docker compose --profile full down
```

## Миграции (Alembic)

Перед миграциями убедитесь, что поднят Postgres и корректен `SSN_DATABASE_URL`.

```bash
cd backend
cp .env.example .env
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```
