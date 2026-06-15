# Резервное копирование и восстановление

Руководство по бэкапу PostgreSQL и медиа-файлов для SkillShare Network.

## Компоненты

| Файл | Назначение |
| --- | --- |
| `scripts/backup.sh` | Горячий дамп БД + архив `backend/uploads/` |
| `scripts/restore.sh` | Очистка БД, накат `.sql`, распаковка медиа |
| `scripts/backup-lib.sh` | Общая логика (`.env`, Docker, pg_dump) |
| `backups/data/` | **Локальные** файлы бэкапов (в `.gitignore`) |
| `backend/uploads/` | Пользовательские вложения |

Параметры подключения читаются из **`backend/.env`** (`SSN_DATABASE_URL`).

## Шаг 1. Бэкап базы данных

```bash
docker compose --profile infra up -d   # если БД в Docker
./scripts/backup.sh
```

Скрипт:
1. Загружает `backend/.env`
2. Выполняет `pg_dump` (через контейнер `db` или локальный `pg_dump`)
3. Сохраняет `backups/data/db_backup_YYYY_MM_DD_HHMMSS.sql`

## Шаг 2. Бэкап медиа

Тот же `./scripts/backup.sh` упаковывает **`backend/uploads/`** в  
`backups/data/media_backup_YYYY_MM_DD_HHMMSS.tar.gz`.

Пустая папка uploads — создаётся минимальный архив (для восстановления структуры).

## Шаг 3. Восстановление «из нуля»

```bash
./scripts/restore.sh backups/data/db_backup_2026_06_10_143022.sql \
  backups/data/media_backup_2026_06_10_143022.tar.gz
```

Скрипт:
1. Запрашивает подтверждение
2. `DROP SCHEMA public CASCADE` — полная очистка БД
3. Накатывает дамп через `psql`
4. Распаковывает медиа в `backend/uploads/`

Если второй аргумент не указан — ищет `media_backup_*` с тем же timestamp.

## Шаг 4. Испытание (симуляция катастрофы)

### 4.1. Подготовка данных

1. Запустите приложение: `docker compose --profile full up` или backend локально
2. Через Swagger/UI: регистрация, объявления, login
3. Положите тестовые файлы в `backend/uploads/` (имитация картинок)

### 4.2. Бэкап

```bash
./scripts/backup.sh
ls -lh backups/data/
```

### 4.3. Имитация аварии

```bash
# Удалить медиа
rm -rf backend/uploads/*

# Очистить БД (или остановить контейнер)
docker compose exec -T db psql -U postgres -d skillshare -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

Проверьте: `curl http://localhost:8000/api/v1/health` — БД недоступна или пуста, API отдаёт ошибки.

### 4.4. Восстановление

```bash
./scripts/restore.sh backups/data/db_backup_<timestamp>.sql
```

Проверьте: health OK, пользователи и объявления на месте, файлы в `backend/uploads/`.

## Production

Для `docker-compose.prod.yml`:

```bash
COMPOSE_FILE=docker-compose.prod.yml \
ENV_FILE=backend/.env \
./scripts/backup.sh
```

Пароль prod — из `.prod-secrets/db_password.txt`; при необходимости задайте `SSN_DATABASE_URL` в `.env` перед бэкапом.

## Git

В репозиторий **не** попадают:
- `backups/data/*.sql`
- `backups/data/*.tar.gz`
- `backend/uploads/*` (кроме `.gitkeep`)

В репозиторий **попадают**: `scripts/*.sh`, `backups/README.md`, эта документация.

## Переменные окружения (опционально)

| Переменная | По умолчанию |
| --- | --- |
| `ENV_FILE` | `backend/.env` |
| `BACKUP_DATA_DIR` | `backups/data` |
| `MEDIA_DIR` | `backend/uploads` |
| `COMPOSE_FILE` | `docker-compose.yml` |
