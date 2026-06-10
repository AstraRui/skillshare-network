#!/bin/bash

set -e

BACKUP_DIR="./backups"
DATE=$(date +"%Y_%m_%d_%H_%M_%S")

mkdir -p "$BACKUP_DIR"

echo "Creating database backup..."

docker compose exec -T postgres pg_dump -U postgres postgres > "$BACKUP_DIR/db_backup_$DATE.sql"

echo "Backup completed"
