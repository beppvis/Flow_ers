.PHONY: help start stop restart logs status clean setup

help: ## Show this help message
	@echo "ANOKHA Logistics Tech Stack - Docker Commands"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

setup: ## Setup environment file from template
	@if [ ! -f .env ]; then \
		cp env.template .env; \
		echo "✅ Created .env file from template"; \
	else \
		echo "⚠️  .env file already exists"; \
	fi

start: setup ## Start all services
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "🌐 ERPNext: http://localhost:8000"
	@echo "🌐 Fleetbase: http://localhost:3000"

stop: ## Stop all services
	docker-compose down
	@echo "✅ Services stopped"

restart: ## Restart all services
	docker-compose restart
	@echo "✅ Services restarted"

logs: ## View logs from all services
	docker-compose logs -f

logs-fleetbase: ## View Fleetbase logs
	docker-compose logs -f fleetbase

logs-frappe: ## View Frappe/ERPNext logs
	docker-compose logs -f frappe

status: ## Show status of all services
	docker-compose ps

shell-fleetbase: ## Open shell in Fleetbase container
	docker-compose exec fleetbase sh

shell-frappe: ## Open shell in Frappe container
	docker-compose exec frappe bash

shell-db: ## Open MariaDB shell
	docker-compose exec mariadb mysql -u frappe -p frappe

clean: ## Stop and remove all containers, networks
	docker-compose down
	@echo "✅ Cleaned up containers and networks"

clean-all: clean ## Remove containers, networks, and volumes (⚠️ deletes data)
	docker-compose down -v
	@echo "⚠️  Removed all volumes (data deleted)"

rebuild: ## Rebuild all containers
	docker-compose up -d --build
	@echo "✅ Containers rebuilt"

update: ## Pull latest images and rebuild
	docker-compose pull
	docker-compose up -d --build
	@echo "✅ Updated and rebuilt containers"

backup-db: ## Backup databases
	@mkdir -p backups
	@echo "📦 Backing up MariaDB..."
	docker-compose exec -T mariadb mysqldump -u frappe -p$$(grep MYSQL_PASSWORD .env | cut -d '=' -f2) frappe > backups/frappe_$$(date +%Y%m%d_%H%M%S).sql
	@echo "📦 Backing up PostgreSQL..."
	docker-compose exec -T postgres pg_dump -U fleetbase fleetbase > backups/fleetbase_$$(date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backups created in backups/ directory"

