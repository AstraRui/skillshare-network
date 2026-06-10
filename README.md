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
| Frontend lint / format | ESLint + Prettier | Проверка React-кода и единый стиль |
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
- `frontend/`: React-приложение (Vite + TailwindCSS)
  - `frontend/src/`: страницы, компоненты, API-клиент
  - `frontend/src/admin/`: UI админ-панели (React)
- `Documentation/`: описание, архитектура, диаграммы, инструкции по секретам
- `secrets/`: локальные файлы для Docker prod (не в git)
- `docker-compose.yml`: PostgreSQL + backend

## Быстрый старт (локально)

Требования: Python 3.12+, [`uv`](https://astral.sh/uv/)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload
```

Открыть:
- `http://localhost:8000/` (SSR страница)
- `http://localhost:8000/api/health` (healthcheck)

### Проверка и форматирование кода

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

Аудит уязвимостей Python-зависимостей:

```bash
make audit-deps
```

| Слой | Линтер | Форматтер |
| --- | --- | --- |
| Backend (Python 3.12) | [Ruff](https://docs.astral.sh/ruff/) (`ruff check`) | Ruff (`ruff format`) |
| Frontend (React + Vite) | [ESLint](https://eslint.org/) (`npm run lint`) | [Prettier](https://prettier.io/) (`npm run format`) |

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
## Backup and Restore

### Create backup

```bash
bash scripts/backup.sh
```

The script creates a PostgreSQL database backup in the `backups/` directory.

### Restore backup

```bash
bash scripts/restore.sh backups/file.sql
```

The restore script imports a previously created database backup.

### Notes

Generated backup files are ignored by Git and must not be committed to the repository.

Ignored files:

```text
backups/
*.sql
*.tar.gz
*.zip
```
