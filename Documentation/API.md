# API-документация

SkillShare Network предоставляет REST API под префиксом `/api/v1/`. Интерактивная документация генерируется автоматически из кода FastAPI (OpenAPI 3).

## Интерактивные интерфейсы

Запустите backend, затем откройте:

| Интерфейс | URL | Возможности |
| --- | --- | --- |
| **Swagger UI** | http://localhost:8000/docs | Просмотр схем, «Try it out», отправка запросов из браузера |
| **ReDoc** | http://localhost:8000/redoc | Читаемая справка по эндпоинтам |
| **OpenAPI JSON** | http://localhost:8000/openapi.json | Импорт в Postman, Insomnia, кодогенерация |

Корень `/` перенаправляет на `/docs` (`backend/app/main.py`).

## Аутентификация

Большинство эндпоинтов требуют заголовок:

```http
Authorization: Bearer <access_token>
```

Токен получается через:

| Метод | Путь | Тело (пример) |
| --- | --- | --- |
| `POST` | `/api/v1/auth/register` | `{ "email", "password", "full_name", ... }` |
| `POST` | `/api/v1/auth/login` | `{ "email", "password" }` |

Ответ login/register содержит `access_token` (JWT, алгоритм HS256, секрет `SSN_SECRET_KEY`).

В Swagger UI: кнопка **Authorize** → введите `Bearer <token>` или только токен (зависит от версии UI).

## Импорт в Postman

1. Postman → **Import** → **Link**
2. URL: `http://localhost:8000/openapi.json` (сервер должен быть запущен)
3. Коллекция создаётся со всеми путями и схемами

Локальная копия OpenAPI: сохраните JSON в `Documentation/openapi/` после экспорта для офлайн-импорта.

```bash
curl -s http://localhost:8000/openapi.json -o Documentation/openapi/openapi.json
```

## Группы эндпоинтов

Базовый URL: `http://<host>:<port>/api/v1`

### Health

| Метод | Путь | Auth | Описание |
| --- | --- | --- | --- |
| `GET` | `/health` | нет | Проверка доступности API |

### Auth

| Метод | Путь | Auth |
| --- | --- | --- |
| `POST` | `/auth/register` | нет |
| `POST` | `/auth/login` | нет |

### Users (профиль)

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/users/me` | да |
| `PATCH` | `/users/me` | да |
| `PUT` | `/users/me/skills` | да |
| `GET` | `/users/me/skills` | да |
| `PATCH` | `/users/me/password` | да |
| `DELETE` | `/users/me` | да |
| `GET` | `/users/me/reviews` | да |

### Skills

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/skills/categories` | нет |
| `GET` | `/skills` | нет |
| `POST` | `/skills` | да |

### Listings (объявления)

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/listings` | опционально |
| `POST` | `/listings` | да |
| `PATCH` | `/listings/{listing_id}` | да |
| `POST` | `/listings/{listing_id}/interests` | да |
| `GET` | `/listings/{listing_id}/interests` | да |
| `GET` | `/listings/me/incoming-interests` | да |

### Exchanges (сделки)

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/exchanges` | да |
| `POST` | `/exchanges/listing/{listing_id}/accept-interest` | да |
| `POST` | `/exchanges/direct` | да |
| `POST` | `/exchanges/{exchange_id}/status` | да |
| `POST` | `/exchanges/{exchange_id}/request-start` | да |
| `POST` | `/exchanges/{exchange_id}/confirm-completion` | да |
| `GET` | `/exchanges/{exchange_id}/messages` | да |
| `POST` | `/exchanges/{exchange_id}/messages` | да |
| `GET` | `/exchanges/{exchange_id}/reviews` | да |
| `POST` | `/exchanges/{exchange_id}/reviews` | да |

### Matches (матчмейкинг)

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/matches` | да |

### Chat

| Метод | Путь | Auth |
| --- | --- | --- |
| `GET` | `/chat/exchanges/{exchange_id}` | да |
| `GET` | `/chat/exchanges/{exchange_id}/messages` | да |
| `PATCH` | `/chat/exchanges/{exchange_id}/messages/{message_id}` | да |
| `DELETE` | `/chat/exchanges/{exchange_id}/messages/{message_id}` | да |

Real-time доставка сообщений — broadcast через WebSocket manager при создании сообщения в exchange (см. `app/ws/manager.py`).

### Admin (роль admin)

| Метод | Путь |
| --- | --- |
| `GET` | `/admin/users`, `/admin/users/{user_id}` |
| `PATCH` | `/admin/users/{user_id}/status` |
| `DELETE` | `/admin/users/{user_id}` |
| `GET` | `/admin/listings`, `PATCH/DELETE` по id |
| `GET` | `/admin/exchanges`, `PATCH/DELETE` по id |
| `GET` | `/admin/chats`, `/admin/chats/{chat_id}/messages` |
| `DELETE` | `/admin/chats/{chat_id}` |
| `GET` | `/admin/reports` |

## Коды ответов и ошибки

Обработчики: `backend/app/api/errors.py`.

| Код | Когда |
| --- | --- |
| `200` | Успешный GET/PATCH |
| `201` | Создание ресурса |
| `204` | Успех без тела (удаление, смена пароля) |
| `400` | Неверные бизнес-правила (например, отклик на своё объявление) |
| `401` | Нет или невалидный JWT |
| `403` | Нет прав (не admin) |
| `404` | Ресурс не найден |
| `422` | Ошибка валидации тела/query (Pydantic) |
| `409` | Конфликт уникальности в БД (`IntegrityError`) |

Формат ошибки (типичный):

```json
{
  "detail": "Missing or invalid Authorization header"
}
```

Валидация (`422`):

```json
{
  "detail": [
    { "loc": ["body", "email"], "msg": "field required", "type": "missing" }
  ]
}
```

## Пример запроса (curl)

```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"YOUR_PASSWORD"}' \
  | jq -r .access_token)

# Профиль
curl -s http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

## Production

За Nginx frontend API доступен по тому же хосту:

```text
https://skillshare.example.com/api/v1/health
https://skillshare.example.com/docs
```

Убедитесь, что прокси передаёт заголовки `Host`, `X-Forwarded-Proto` (см. [DEPLOYMENT.md](./DEPLOYMENT.md)).
