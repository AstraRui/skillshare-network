Архитектура проекта
Проект разделён на две независимые части: бэкенд (FastAPI) и фронтенд (React + Vite). Связь через REST API и WebSocket.

Бэкенд (FastAPI)
FastAPI — веб-фреймворк, обрабатывает HTTP/WebSocket.

SQLAlchemy 2.0 (async) — ORM для PostgreSQL.

Alembic — миграции БД.

Redis — кэш и брокер сообщений для WebSocket.

Pydantic — валидация данных, сериализация.

Фронтенд (React + Vite + TailwindCSS + FlyonUI)
React 18 (с Hooks, Context API, React Router) — построение интерфейса.

Vite — быстрая сборка, горячая замена модулей (HMR).

TailwindCSS + FlyonUI — стилизация и готовые UI-компоненты.

WebSocket API — для real-time чатов.


Поток данных (пример создания сделки)
Пользователь А публикует объявление через React-форму → POST /api/v1/listings.

Пользователь Б отправляет отклик → POST /api/listings/{id}/interests.

Автор А принимает отклик → POST /api/exchanges → создаётся Exchange и Chat.

Участники общаются через WebSocket чат (встроен в React).

После завершения обмена оба подтверждают через React-кнопки → PATCH /api/exchanges/{id}/complete.

Система предлагает оставить отзыв (React-форма) → POST /api/reviews.


Технологический стек
Слой	Технологии
Бэкенд	Python 3.12, FastAPI
ORM	SQLAlchemy 2.0 (async), Alembic
База данных	PostgreSQL 16+
Кэш / брокер чатов	Redis 7+
Фронтенд-фреймворк	React 18 + Vite
UI-компоненты	TailwindCSS + FlyonUI
Real-time	WebSockets (FastAPI + Redis pub/sub)
Аутентификация	JWT (secure cookies / Bearer)
Линтинг и форматирование	Ruff (бэкенд), ESLint + Prettier (фронтенд)
Безопасность зависимостей	pip-audit (Python), npm audit (frontend)
SAST (бэкенд)	Bandit
Контейнеризация	Docker, Docker Compose
CI/CD	GitHub Actions
