#!/bin/sh
# Читаем Docker secrets и экспортируем как переменные окружения
if [ -f /run/secrets/secret_key ]; then
    export SSN_SECRET_KEY=$(cat /run/secrets/secret_key)
fi

if [ -f /run/secrets/db_password ]; then
    DB_PASSWORD=$(cat /run/secrets/db_password)
    export SSN_DATABASE_URL="postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/skillshare"
fi

exec "$@"
