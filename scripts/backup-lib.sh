#!/usr/bin/env bash
# Общие функции для backup.sh и restore.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

ENV_FILE="${ENV_FILE:-$ROOT_DIR/backend/.env}"
BACKUP_DATA_DIR="${BACKUP_DATA_DIR:-$ROOT_DIR/backups/data}"
MEDIA_DIR="${MEDIA_DIR:-$ROOT_DIR/backend/uploads}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/docker-compose.yml}"
DB_SERVICE="${DB_SERVICE:-db}"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

die() {
  log "ERROR: $*" >&2
  exit 1
}

load_env() {
  if [[ ! -f "$ENV_FILE" ]]; then
    die "Файл окружения не найден: $ENV_FILE (скопируйте backend/.env.example → backend/.env)"
  fi

  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a

  : "${SSN_DATABASE_URL:?SSN_DATABASE_URL не задан в $ENV_FILE}"
}

# postgresql+asyncpg://user:pass@host:5432/dbname → переменные DB_*
parse_database_url() {
  local url="$SSN_DATABASE_URL"
  url="${url#postgresql+asyncpg://}"
  url="${url#postgresql://}"

  local userpass hostpart
  userpass="${url%%@*}"
  hostpart="${url#*@}"

  DB_USER="${userpass%%:*}"
  DB_PASS="${userpass#*:}"
  DB_NAME="${hostpart#*/}"
  DB_NAME="${DB_NAME%%\?*}"

  local hostport="${hostpart%%/*}"
  DB_HOST="${hostport%%:*}"
  DB_PORT="${hostport#*:}"
  if [[ "$DB_PORT" == "$hostport" ]]; then
    DB_PORT="5432"
  fi

  # В Docker Compose сервис называется db, с хоста подключаемся через localhost
  if [[ "$DB_HOST" == "db" ]]; then
    DB_HOST="localhost"
  fi
}

compose_cmd() {
  if [[ -f "$COMPOSE_FILE" ]]; then
    docker compose -f "$COMPOSE_FILE" "$@"
  else
    docker compose "$@"
  fi
}

is_db_container_running() {
  compose_cmd ps "$DB_SERVICE" --status running -q 2>/dev/null | grep -q .
}

run_pg_dump() {
  local output_file="$1"
  if is_db_container_running; then
    log "pg_dump через Docker (сервис $DB_SERVICE)..."
    compose_cmd exec -T "$DB_SERVICE" \
      pg_dump -U "$DB_USER" -d "$DB_NAME" --no-owner --no-acl --clean --if-exists \
      >"$output_file"
  else
    if ! command -v pg_dump >/dev/null 2>&1; then
      die "pg_dump не найден. Запустите PostgreSQL: docker compose --profile infra up -d"
    fi
    log "pg_dump локально ($DB_HOST:$DB_PORT/$DB_NAME)..."
    PGPASSWORD="$DB_PASS" pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
      --no-owner --no-acl --clean --if-exists >"$output_file"
  fi
}

run_psql_file() {
  local input_file="$1"
  if is_db_container_running; then
    log "Восстановление SQL через Docker..."
    compose_cmd exec -T "$DB_SERVICE" \
      psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <"$input_file"
  else
    if ! command -v psql >/dev/null 2>&1; then
      die "psql не найден. Запустите PostgreSQL: docker compose --profile infra up -d"
    fi
    log "Восстановление SQL локально..."
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
      -v ON_ERROR_STOP=1 <"$input_file"
  fi
}

reset_database() {
  local reset_sql
  reset_sql="$(mktemp)"
  cat >"$reset_sql" <<'SQL'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
SQL

  if is_db_container_running; then
    log "Очистка базы (DROP SCHEMA public CASCADE)..."
    compose_cmd exec -T "$DB_SERVICE" \
      psql -U "$DB_USER" -d "$DB_NAME" -v ON_ERROR_STOP=1 <"$reset_sql"
  else
    PGPASSWORD="$DB_PASS" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
      -v ON_ERROR_STOP=1 <"$reset_sql"
  fi
  rm -f "$reset_sql"
}

archive_media() {
  local output_file="$1"
  mkdir -p "$MEDIA_DIR"
  log "Архивация медиа: $MEDIA_DIR"
  tar -czf "$output_file" -C "$MEDIA_DIR" .
}

restore_media() {
  local archive_file="$1"
  mkdir -p "$MEDIA_DIR"
  log "Восстановление медиа в $MEDIA_DIR"
  rm -rf "${MEDIA_DIR:?}/"*
  tar -xzf "$archive_file" -C "$MEDIA_DIR"
}
