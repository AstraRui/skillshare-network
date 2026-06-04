# Секреты для production (Docker)

Файлы с паролями **не хранятся в git**. Перед первым запуском `docker-compose.prod.yml` создайте локальный каталог `.prod-secrets/` в корне репозитория.

## Создание секретов

```bash
mkdir -p .prod-secrets
openssl rand -hex 32 > .prod-secrets/secret_key.txt
echo "YOUR_STRONG_DB_PASSWORD" > .prod-secrets/db_password.txt
chmod 600 .prod-secrets/*.txt
```

| Файл | Назначение | Демо-содержимое (не использовать в prod) |
| --- | --- | --- |
| `.prod-secrets/secret_key.txt` | `SSN_SECRET_KEY` для JWT | 64-символьная hex-строка |
| `.prod-secrets/db_password.txt` | Пароль пользователя `postgres` в БД | `YOUR_STRONG_DB_PASSWORD` |

Каталог `.prod-secrets/` добавлен в `.gitignore`.

## Как это работает

1. `docker-compose.prod.yml` монтирует файлы как [Docker secrets](https://docs.docker.com/compose/how-tos/use-secrets/).
2. `backend/entrypoint.sh` читает `/run/secrets/secret_key` и `/run/secrets/db_password` и экспортирует `SSN_SECRET_KEY` и `SSN_DATABASE_URL`.
3. Сервис `backend` не публикует порт наружу — доступ только через Nginx во frontend-контейнере.

## Запуск production-стека

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Проверка:

```bash
docker compose -f docker-compose.prod.yml ps
curl -s http://localhost/api/v1/health
```

Приложение слушает порт **80** на хосте (frontend + встроенный Nginx).

## Ротация секретов

1. Сгенерировать новые файлы в `.prod-secrets/`
2. `docker compose -f docker-compose.prod.yml down`
3. При смене пароля БД — обновить пароль в PostgreSQL или пересоздать том `pg_data` (потеря данных!)
4. `docker compose -f docker-compose.prod.yml up -d`

Смена `SSN_SECRET_KEY` инвалидирует все выданные JWT — пользователям потребуется повторный вход.

## Альтернатива без файлов

На выделенном сервере секреты можно передавать через оркестратор (Kubernetes Secrets, Vault). В этом случае адаптируйте `entrypoint.sh` или задайте `SSN_SECRET_KEY` и `SSN_DATABASE_URL` напрямую в `environment` сервиса `backend` (не рекомендуется хранить в plain text в compose-файле).
