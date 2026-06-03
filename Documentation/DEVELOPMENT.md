# Разработка и качество кода

Единые команды из корня репозитория (см. `Makefile`).

## Установка инструментов

```bash
make install-tools
```

- Backend: `uv sync --dev` (Ruff, pytest, pip-audit, Bandit)
- Frontend: `npm ci` (ESLint, Prettier)

## Линт и форматирование

| Команда | Действие |
| --- | --- |
| `make lint` | Проверка без записи (как в CI) |
| `make format` | Автоформатирование |
| `make lint-fix` | Lint с автоисправлением + формат фронта |

### Backend (Python 3.12)

| Инструмент | Назначение | Команда |
| --- | --- | --- |
| [Ruff](https://docs.astral.sh/ruff/) | Линт (E, F, I, UP, B, SIM) + формат | `uv run ruff check .` / `uv run ruff format .` |

Конфиг: `backend/pyproject.toml` (`[tool.ruff]`).

### Frontend (React + Vite)

| Инструмент | Назначение | Команда |
| --- | --- | --- |
| [ESLint](https://eslint.org/) | Статический анализ JS/JSX | `npm run lint` |
| [Prettier](https://prettier.io/) | Форматирование | `npm run format` / `npm run format:check` |

Конфиг: `frontend/eslint.config.js`, `frontend/.prettierrc`.

## Безопасность

| Команда | Что проверяет |
| --- | --- |
| `make security` | Полный аудит backend + frontend |
| `make audit-deps` | Синоним `make security` |

### Backend

| Инструмент | Назначение | Команда |
| --- | --- | --- |
| [pip-audit](https://pypi.org/project/pip-audit/) | Известные CVE в Python-зависимостях | `uv run pip-audit` |
| [Bandit](https://bandit.readthedocs.io/) | SAST по коду `app/` | `uv run bandit -r app -c pyproject.toml` |

Конфиг Bandit: `[tool.bandit]` в `backend/pyproject.toml`.

### Frontend

| Инструмент | Назначение | Команда |
| --- | --- | --- |
| `npm audit` | CVE в npm-зависимостях | `npm run audit` (порог: `high`) |

## Pre-commit

Перед коммитом (быстрые проверки: Ruff, ESLint, Prettier, Bandit):

```bash
pip install pre-commit   # или: uv tool install pre-commit
pre-commit install
pre-commit run --all-files
```

Аудит зависимостей (`pip-audit`, `npm audit`) в pre-commit **не** включён — он медленнее и гоняется в CI и через `make security`.

Конфиг: `.pre-commit-config.yaml`.

## CI (GitHub Actions)

Файл: `.github/workflows/ci.yml`

| Job | Проверки |
| --- | --- |
| `backend-lint` | Ruff check + format --check |
| `backend-security` | pip-audit, Bandit |
| `backend-tests` | pytest |
| `frontend-lint` | ESLint, Prettier check |
| `frontend-security` | npm audit |
| `docker-build` | Сборка образов (после успеха остальных) |

## Структура frontend (после уборки)

- Одна админка: `src/pages/AdminPage.jsx`, маршрут `/admin`, API через `src/api/client.js`
- Компоненты по доменам: `src/components/{auth,deals,layout,listings,network,ui}/`
- Удалены дубликаты: отдельный `admin-panel.html`, папка-заглушка `src/admin/`, второй mount chat API на backend

## Структура backend API

Все REST-эндпоинты v1 — только под префиксом `/api/v1/` (агрегатор `app/api/v1/router.py`).
