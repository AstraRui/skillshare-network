.PHONY: help lint format lint-fix audit-deps install-tools

help:
	@echo "Targets:"
	@echo "  make install-tools  — установить dev-зависимости (uv + npm)"
	@echo "  make lint           — проверка стиля (ruff + eslint + prettier)"
	@echo "  make format         — автоформатирование (ruff + prettier)"
	@echo "  make lint-fix       — lint с автоисправлением где возможно"
	@echo "  make audit-deps     — аудит уязвимостей в Python-зависимостях"

install-tools:
	cd backend && uv sync --dev
	cd frontend && npm ci

lint:
	cd backend && uv run ruff check .
	cd backend && uv run ruff format --check .
	cd frontend && npm run lint
	cd frontend && npm run format:check

format:
	cd backend && uv run ruff format .
	cd backend && uv run ruff check --fix .
	cd frontend && npm run format

lint-fix:
	cd backend && uv run ruff check --fix .
	cd backend && uv run ruff format .
	cd frontend && npm run lint:fix
	cd frontend && npm run format

audit-deps:
	cd backend && uv run pip-audit
