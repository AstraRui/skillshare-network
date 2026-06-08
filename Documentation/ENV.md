# Переменные окружения

Справочник настроек с **маскированными** демо-значениями. Реальные секреты не коммитятся — копируйте `.env.example` в `.env` и подставьте свои данные.

## Backend

Файл: `backend/.env` (шаблон: `backend/.env.example`).  
Все переменные читаются через Pydantic Settings с префиксом `SSN_` (см. `backend/app/core/settings.py`).

| Переменная в `.env` | Поле в коде | Пример (демо) | Описание |
| --- | --- | --- | --- |
| `SSN_ENVIRONMENT` | `environment` | `local` | Окружение: `local`, `docker`, `production` — влияет на логирование и поведение при отладке |
| `SSN_SECRET_KEY` | `secret_key` | `YOUR_SECRET_KEY_MIN_32_CHARS` | Ключ подписи JWT. В production — случайная строка ≥ 32 символов |
| `SSN_DATABASE_URL` | `database_url` | `postgresql+asyncpg://db_user:db_pass@db_host:5432/skillshare` | URL PostgreSQL (драйвер `asyncpg`) |
| `SSN_REDIS_URL` | `redis_url` | `redis://redis_host:6379/0` | URL Redis |
| `SSN_PUBLIC_BASE_URL` | `public_base_url` | `https://app.example.com` | Публичный базовый URL приложения (опционально) |
| `SSN_LOG_LEVEL` | `log_level` | `INFO` | Уровень логирования: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `SSN_LOG_DIR` | `log_dir` | `logs` | Каталог файлов логов (в `.gitignore`) |
| `SSN_LOG_FILE` | `log_file` | `app.log` | Имя основного лог-файла |
| `SSN_LOG_MAX_BYTES` | `log_max_bytes` | `10485760` | Ротация: макс. размер файла (10 МБ) |
| `SSN_LOG_BACKUP_COUNT` | `log_backup_count` | `5` | Ротация: число архивных копий |

Подробнее: [LOGGING.md](./LOGGING.md).

### Примеры по средам

**Локальная разработка (PostgreSQL на localhost):**

```env
SSN_ENVIRONMENT=local
SSN_SECRET_KEY=dev-only-change-me
SSN_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/skillshare
SSN_REDIS_URL=redis://localhost:6379/0
```

**Docker Compose (dev profile `full`):**

Задаётся в `docker-compose.yml` (перекрывает `.env`):

```env
SSN_ENVIRONMENT=docker
SSN_DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/skillshare
SSN_REDIS_URL=redis://redis:6379/0
```

**Production (через Docker secrets + entrypoint):**

| Источник | Переменная после старта | Пример |
| --- | --- | --- |
| Файл `.prod-secrets/secret_key.txt` | `SSN_SECRET_KEY` | `a1b2c3…` (64 hex от `openssl rand -hex 32`) |
| Файл `.prod-secrets/db_password.txt` | `SSN_DATABASE_URL` | `postgresql+asyncpg://postgres:***@db:5432/skillshare` |
| `docker-compose.prod.yml` | `SSN_ENVIRONMENT` | `production` |
| `docker-compose.prod.yml` | `SSN_REDIS_URL` | `redis://redis:6379/0` |

См. [PRODUCTION-SECRETS.md](./PRODUCTION-SECRETS.md).

### Разбор `SSN_DATABASE_URL`

| Часть URL | Демо | Описание |
| --- | --- | --- |
| Схема | `postgresql+asyncpg` | Обязательно для async SQLAlchemy |
| Пользователь | `db_user` | Роль PostgreSQL |
| Пароль | `YOUR_DB_PASSWORD` | Пароль (в prod — из secret-файла) |
| Хост | `localhost` / `db` | `localhost` локально, `db` — имя сервиса в Compose |
| Порт | `5432` | Стандартный порт PostgreSQL |
| База | `skillshare` | Имя БД |

---

## Frontend

Файл: `frontend/.env` (шаблон: `frontend/.env.example`).  
Используется только на этапе **разработки** (Vite).

| Переменная | Пример (демо) | Описание |
| --- | --- | --- |
| `VITE_PROXY_TARGET` | `http://localhost:8000` | Backend для прокси `/api` в `vite.config.js` |

В production-сборке фронтенд обращается к API через тот же origin (Nginx проксирует `/api/` → backend). Отдельный `.env` на prod для SPA не требуется.

---

## PostgreSQL (Docker Compose)

Задаются в `docker-compose.yml` / `docker-compose.prod.yml`, не в `SSN_*`:

| Переменная | Dev (демо) | Prod |
| --- | --- | --- |
| `POSTGRES_USER` | `postgres` | `postgres` |
| `POSTGRES_PASSWORD` | `postgres` | из `POSTGRES_PASSWORD_FILE` |
| `POSTGRES_DB` | `skillshare` | `skillshare` |

---

## Чеклист для нового окружения

1. Скопировать `backend/.env.example` → `backend/.env`
2. Заменить `SSN_SECRET_KEY` на уникальный секрет
3. Указать корректный `SSN_DATABASE_URL`
4. При локальном фронте: `frontend/.env` с `VITE_PROXY_TARGET`
5. Выполнить `uv run alembic upgrade head`
6. Для prod: создать `.prod-secrets/` по [PRODUCTION-SECRETS.md](./PRODUCTION-SECRETS.md)
