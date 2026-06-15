#!/usr/bin/env bash
# Горячий бэкап PostgreSQL + архив медиа-файлов (uploads)
#
# Использование:
#   ./scripts/backup.sh
#   ENV_FILE=backend/.env ./scripts/backup.sh
#
# Результат: backups/data/db_backup_YYYY_MM_DD_HHMMSS.sql
#            backups/data/media_backup_YYYY_MM_DD_HHMMSS.tar.gz

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/backup-lib.sh
source "$SCRIPT_DIR/backup-lib.sh"

main() {
  load_env
  parse_database_url

  local timestamp
  timestamp="$(date '+%Y_%m_%d_%H%M%S')"
  mkdir -p "$BACKUP_DATA_DIR"

  local sql_file="$BACKUP_DATA_DIR/db_backup_${timestamp}.sql"
  local media_file="$BACKUP_DATA_DIR/media_backup_${timestamp}.tar.gz"

  log "=== SkillShare Network — резервное копирование ==="
  log "База: $DB_NAME @ $DB_HOST:$DB_PORT (user: $DB_USER)"
  log "Медиа: $MEDIA_DIR"

  run_pg_dump "$sql_file"
  log "SQL дамп: $sql_file ($(du -h "$sql_file" | cut -f1))"

  archive_media "$media_file"
  log "Медиа-архив: $media_file ($(du -h "$media_file" | cut -f1))"

  log "=== Бэкап завершён успешно ==="
  log "Восстановление: ./scripts/restore.sh $sql_file $media_file"
}

main "$@"
