COMPOSE = docker compose

.DEFAULT_GOAL := help

.PHONY: help init up down restart build logs ps test shell-backend shell-frontend db migrate seed

help: ## Показать команды
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-18s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## Создать .env из примера
	@test -f .env || cp .env.example .env

up: init ## Собрать и запустить frontend, backend и БД
	$(COMPOSE) up -d --build

down: ## Остановить проект, сохранив данные БД
	$(COMPOSE) down

restart: ## Перезапустить сервисы
	$(COMPOSE) restart

build: init ## Пересобрать образы
	$(COMPOSE) build

logs: ## Смотреть логи всех сервисов
	$(COMPOSE) logs -f --tail=100

ps: ## Показать состояние контейнеров
	$(COMPOSE) ps

test: init ## Запустить API-тесты в контейнере
	$(COMPOSE) run --rm backend pytest backend/tests/test_api.py -q

shell-backend: ## Открыть shell backend-контейнера
	$(COMPOSE) exec backend sh

shell-frontend: ## Открыть shell frontend-контейнера
	$(COMPOSE) exec frontend sh

db: ## Открыть psql
	$(COMPOSE) exec postgres sh -c 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"'

migrate: ## Применить миграции
	$(COMPOSE) exec backend alembic upgrade head

seed: ## Добавить demo-данные
	$(COMPOSE) exec backend python database/seeds/demo_users.py
