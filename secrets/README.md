# secrets/

Папка для Docker secrets (production).
Файлы в этой папке **не коммитятся** (см. .gitignore).

## Создание секретов перед запуском prod

```bash
mkdir -p secrets
echo "$(openssl rand -hex 32)" > secrets/secret_key.txt
echo "strongpassword" > secrets/db_password.txt
chmod 600 secrets/*.txt
```

## Использование

```bash
docker compose -f docker-compose.prod.yml up -d
```
