# Логирование и трассировка

Сквозное логирование бэкенда: консоль (Docker stdout) + файл с ротацией, уровни INFO/WARNING/ERROR/CRITICAL, stack trace при сбоях.

## Архитектура

| Модуль | Назначение |
| --- | --- |
| `backend/app/logging/logging_config.py` | Console + `RotatingFileHandler`, формат строки |
| `backend/app/logging/logging_middleware.py` | HTTP-запросы: метод, путь, статус, duration |
| `backend/app/db/session.py` | Подключение к PostgreSQL, CRITICAL при сбое транзакции |
| `backend/app/services/auth.py` | Вход, регистрация, выдача JWT |
| `backend/app/api/deps.py` | Валидация Bearer JWT |
| `backend/app/api/errors.py` | HTTP и integrity-ошибки |

## Формат строки

```
[2026-06-04 12:00:00] [INFO] [auth.py:72] - Login successful user_id=1 role=user JWT issued
```

HTTP-запросы дополнительно содержат `request_id`, `method`, `path`, `status_code`, `duration`.

## Каналы вывода

| Handler | Куда | Зачем |
| --- | --- | --- |
| `StreamHandler` | stdout | Docker daemon перехватывает логи контейнера |
| `RotatingFileHandler` | `logs/app.log` | Локальный архив на диске |

Ротация (по умолчанию): **10 МБ** на файл, **5** архивных копий (`app.log.1` …).

Папка `logs/` в `.gitignore` — в репозиторий не попадает.

## Переменные окружения

| Переменная | По умолчанию | Описание |
| --- | --- | --- |
| `SSN_LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `SSN_LOG_DIR` | `logs` | Каталог логов (относительно `backend/`) |
| `SSN_LOG_FILE` | `app.log` | Имя файла |
| `SSN_LOG_MAX_BYTES` | `10485760` | Макс. размер файла до ротации (10 МБ) |
| `SSN_LOG_BACKUP_COUNT` | `5` | Число архивных файлов |

## Покрытие по зонам

### PostgreSQL

- **INFO** — успешное подключение при старте (`check_database_connection`)
- **INFO** — создание объявления, отзыва
- **CRITICAL** — недоступна БД при старте или healthcheck; сбой commit/rollback транзакции (stack trace)
- **ERROR** — integrity-ошибки, сбой регистрации/отзыва

### Аутентификация

- **INFO** — попытка и успех login/register, выдача JWT
- **WARNING** — отсутствует заголовок Authorization, истёкший токен, заблокированный пользователь
- **ERROR** — неверный пароль, невалидная подпись JWT

### Внешние API

В проекте **нет** исходящих интеграций (Telegram, почта, карты). Входящие HTTP-запросы логирует `logging_middleware`.

## Тестирование (пара 6)

### Штатный режим

```bash
cd backend
uv sync
cp .env.example .env
docker compose --profile infra up -d   # или локальный Postgres
uv run uvicorn app.main:app --reload
```

1. Откройте http://localhost:8000/docs
2. Выполните: `POST /auth/login`, `GET /listings`, `POST /listings`
3. Проверьте **консоль** и файл `backend/logs/app.log` — записи **INFO**

### Эмуляция падения БД

**Вариант А:** остановите PostgreSQL:

```bash
docker compose stop db
curl http://localhost:8000/api/v1/health
docker compose start db
```

В `logs/app.log` появится **CRITICAL** с полным stack trace. API вернёт JSON с `"db": "error: ..."`, не «белый экран».

**Вариант Б:** укажите неверный пароль в `SSN_DATABASE_URL`, перезапустите backend — при старте **CRITICAL** в логе.

### Просмотр логов в Docker

```bash
docker compose logs -f backend
```

## Уровни (шпаргалка)

| Уровень | Примеры в проекте |
| --- | --- |
| INFO | Старт приложения, login OK, listing created, HTTP 200 |
| WARNING | HTTP 4xx, истёкший JWT, медленные отмены запросов |
| ERROR | Неверный пароль, invalid JWT, integrity error |
| CRITICAL | PostgreSQL недоступна, транзакция откатилась |
