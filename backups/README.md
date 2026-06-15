# Резервные копии (локально)

Сюда скрипты складывают **готовые** дампы и архивы. Каталог `data/` в `.gitignore` — на GitHub попадают только `.sh` скрипты из `scripts/`.

## Быстрый старт

```bash
# 1. Поднять PostgreSQL
docker compose --profile infra up -d

# 2. Создать бэкап
chmod +x scripts/backup.sh scripts/restore.sh
./scripts/backup.sh

# 3. Восстановить (после «катастрофы»)
./scripts/restore.sh backups/data/db_backup_YYYY_MM_DD_HHMMSS.sql
```

Подробнее: [Documentation/BACKUP.md](../Documentation/BACKUP.md).

## Структура после backup

```
backups/data/
├── db_backup_2026_06_10_143022.sql
└── media_backup_2026_06_10_143022.tar.gz
```

Имена содержат дату и время (`YYYY_MM_DD_HHMMSS`).
