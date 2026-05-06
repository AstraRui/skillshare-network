## SkillShare Network

SkillShare Network — инфраструктурное решение для автоматизации бартера в B2B и P2P сегментах. Платформа агрегирует профили навыков и интеллектуальных услуг, используя алгоритм многофакторного поиска для формирования цепочек взаимной выгоды. Стек включает высокопроизводительный REST API и событийную архитектуру на WebSockets для мгновенной коммуникации участников.

## Технологический стек

| Слой | Технология | Почему |
| --- | --- | --- |
| Backend | Python 3.12 + FastAPI | Максимальная скорость, асинхронность, мощная типизация (Pydantic) |
| Linter / Formatter | Ruff | Заменяет Flake8, Black и Isort. Молниеносная проверка кода |
| Frontend (Engine) | Jinja2 + HTMX | No-JS подход: логика на бэкенде, динамика через HTML-атрибуты |
| UI-компоненты | TailwindCSS + FlyonUI | Профессиональный UI на чистом HTML/CSS, без Node.js рантайма |
| Client Logic | Alpine.js | Минималистичный JS (как Vue, но в HTML) для простых UI-эффектов |
| ORM | SQLAlchemy 2.0 + Alembic | Работа со сложным SQL и рекурсиями для матчинга цепочек |
| База данных | PostgreSQL 16+ | Реляционная классика, идеальна для графовых запросов (CTE) |
| Кэш / Чат | Redis + WebSockets | Быстрый кеш и real-time транспорт для сообщений |
| Auth | Secure Cookies + JWT | Безопаснее и проще для SSR-приложений, чем чистый JWT в LocalStorage |
| Ops | Docker + GitHub Actions | Стандарт индустрии для контейнеризации и автоматизации |

## Структура репозитория

- `backend/`: FastAPI-приложение (SSR Jinja2/HTMX), DB слой и миграции Alembic
- `frontend/`: зарезервировано (если появится отдельная сборка/ассеты)
- `docker-compose.yml`: PostgreSQL + Redis + backend

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

### Ruff

```bash
cd backend
uv run ruff check .
uv run ruff format .
```

## Запуск через Docker

```bash
docker compose up --build
```

## Миграции (Alembic)

Перед миграциями убедитесь, что поднят Postgres и корректен `SSN_DATABASE_URL`.

```bash
cd backend
cp .env.example .env
uv run alembic revision --autogenerate -m "init"
uv run alembic upgrade head
```

