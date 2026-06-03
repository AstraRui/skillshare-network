.PHONY: help install-tools lint format lint-fix security audit-deps

help:
	@echo "Targets:"
	@echo "  make install-tools  — dev-зависимости (uv + npm)"
	@echo "  make lint           — линтеры и формат (ruff, eslint, prettier)"
	@echo "  make format         — автоформатирование"
	@echo "  make lint-fix       — lint с автоисправлением"
	@echo "  make security       — аудит уязвимостей + SAST (pip-audit, bandit, npm audit)"
	@echo "  make audit-deps     — то же, что make security"

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

CACHE_DIR := $(CURDIR)/.cache

security audit-deps:
	@mkdir -p $(CACHE_DIR)/pip-audit
	cd backend && uv run pip-audit --cache-dir $(CACHE_DIR)/pip-audit
	cd backend && uv run bandit -r app -c pyproject.toml
	cd frontend && npm run audit
