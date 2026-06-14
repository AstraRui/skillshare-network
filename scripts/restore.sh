#!/usr/bin/env bash
# Восстановление БД и медиа из бэкапа
#
# Использование:
#   ./scripts/restore.sh backups/data/db_backup_2026_06_10_143022.sql
#   ./scripts/restore.sh backups/data/db_backup_2026_06_10_143022.sql backups/data/media_backup_2026_06_10_143022.tar.gz
#
# Если медиа-архив не указан — ищется файл с тем же timestamp в имени.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/backup-lib.sh
source "$SCRIPT_DIR/backup-lib.sh"

usage() {
  cat <<EOF
Usage: $0 <db_backup.sql> [media_backup.tar.gz]

Примеры:
  $0 backups/data/db_backup_2026_06_10_143022.sql
  $0 backups/data/db_backup_2026_06_10_143022.sql backups/data/media_backup_2026_06_10_143022.tar.gz
EOF
}

find_media_for_sql() {
  local sql_path="$1"
  local base
  base="$(basename "$sql_path" .sql)"
  local ts="${base#db_backup_}"
  local candidate="$BACKUP_DATA_DIR/media_backup_${ts}.tar.gz"
  if [[ -f "$candidate" ]]; then
    echo "$candidate"
  fi
}

main() {
  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  local sql_file="$1"
  local media_file="${2:-}"

  [[ -f "$sql_file" ]] || die "SQL дамп не найден: $sql_file"

  if [[ -z "$media_file" ]]; then
    media_file="$(find_media_for_sql "$sql_file" || true)"
  fi

  load_env
  parse_database_url

  log "=== SkillShare Network — восстановление ==="
  log "SQL: $sql_file"
  if [[ -n "$media_file" && -f "$media_file" ]]; then
    log "Медиа: $media_file"
  else
    log "Медиа-архив не найден — восстанавливается только БД"
  fi

  read -r -p "Очистить текущую БД и восстановить из дампа? [y/N] " confirm
  if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log "Отменено."
    exit 0
  fi

  reset_database
  run_psql_file "$sql_file"
  log "База данных восстановлена."

  if [[ -n "$media_file" && -f "$media_file" ]]; then
    restore_media "$media_file"
    log "Медиа-файлы восстановлены."
  fi

  log "=== Восстановление завершено ==="
  log "Перезапустите backend при необходимости: uv run uvicorn app.main:app --reload"
}

main "$@"
