# Секреты для production (Docker)

Папка `secrets/` в корне репозитория — только для **локальных файлов** с паролями при запуске `docker-compose.prod.yml`. Эти файлы **не коммитятся** (см. `.gitignore`).

## Создание перед первым prod-запуском

```bash
mkdir -p secrets
echo "$(openssl rand -hex 32)" > secrets/secret_key.txt
echo "strongpassword" > secrets/db_password.txt
chmod 600 secrets/*.txt
```

## Запуск

```bash
docker compose -f docker-compose.prod.yml up -d
```

См. также `docker-compose.prod.yml` и `backend/entrypoint.sh`.
