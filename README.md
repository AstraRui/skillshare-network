# SkillShare Network

SkillShare Network — инфраструктурное решение для автоматизации бартера в B2B и P2P сегментах. Платформа агрегирует профили навыков и интеллектуальных услуг, используя алгоритм многофакторного поиска для формирования цепочек взаимной выгоды. 

Проект построен на современной **архитектуре разделенного фронтенда (SPA) и бэкенда (REST API)**, что обеспечивает масштабируемость и лучший пользовательский опыт.

## Технологический стек

| Слой | Технология | Почему |
| --- | --- | --- |
| **Backend** | Python 3.12 + FastAPI | Асинхронность, высокая производительность, Pydantic v2 |
| **Frontend** | React 18 + Vite | Быстрый UI, компонентный подход, экосистема ассетов |
| **Linter / Formatter** | Ruff | Молниеносная проверка и форматирование Python кода |
| **UI-компоненты** | TailwindCSS + HeadlessUI | Гибкая стилизация и доступные компоненты |
| **ORM** | SQLAlchemy 2.0 + Alembic | Типизированная работа с БД, поддержка сложных CTE запросов |
| **База данных** | PostgreSQL 16+ | Надежное хранение данных и сложных связей |
| **Кэш / Чат** | Redis + WebSockets | Real-time коммуникация и оптимизация запросов |
| **Auth** | JWT + Secure Cookies | Безопасная авторизация через HTTP-only cookies |
| **Ops** | Docker + GitHub Actions | Контейнеризация и автоматизация CI/CD |

## Структура репозитория

- `backend/` — FastAPI приложение (REST API), логика матчинга и миграции Alembic.
- `frontend/` — SPA приложение на React (Vite), работающее с API.
- `docker-compose.yml` — Инфраструктура: PostgreSQL + Redis + Backend + Frontend.

## Быстрый старт (локально)

### 1. Запуск Backend
Требования: Python 3.12+, [`uv`]([https://astral.sh/uv/](https://astral.sh/uv/))
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`

### 2. Запуск Frontend
Требования: Node.js 18+, npm
```bash
cd frontend
npm install
npm run dev
```
- Web: `http://localhost:5173`

---

## Миграции (Alembic)

```bash
cd backend
# Настройте .env (DATABASE_URL)
uv run alembic upgrade head
```

## Разработка и качество кода

### Python (Ruff)
```bash
cd backend
uv run ruff check . --fix  # Проверка и авто-исправление
uv run ruff format .       # Форматирование
```

### Frontend (Lint)
```bash
cd frontend
npm run lint
```

## Запуск в Docker (Полный стек)

```bash
docker compose up --build
```

---

### Что конкретно изменилось в README:
1.  **Заменил Jinja2/HTMX на React/Vite** в таблице стека.
2.  **Обновил описание Frontend**: теперь это не просто "резерв", а полноценное SPA.
3.  **Разделил "Быстрый старт"**: добавил шаги для запуска Node.js проекта.
4.  **Скорректировал описание Auth**: для React + FastAPI чаще используется связка JWT в Cookies (или Bearer Token), а не классические SSR сессии.
5.  **Добавил ссылки на порты**: 8000 для API и 5173 для Vite.