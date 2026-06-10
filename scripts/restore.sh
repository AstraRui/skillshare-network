#!/bin/bash

set -e

if [ -z "$1" ]; then
  echo "Usage: ./scripts/restore.sh backup.sql"
  exit 1
fi

DB_BACKUP_FILE="$1"

echo "Restoring database..."

cat "$DB_BACKUP_FILE" | docker compose exec -T postgres psql -U postgres postgres

echo "Restore completed"
