# GeoDjango Simple Template — single prod build path.
# No dev/prod split; one Dockerfile, one compose.yaml.

.PHONY: help build up down restart logs shell pg-shell migrate makemigrations \
        collectstatic createsuperuser test clean status runserver

.DEFAULT_GOAL := help

DC := docker compose
APP_DIR := app/hellodjango

help:  ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-18s %s\n", $$1, $$2}'

# --- docker compose targets ---

build:  ## Build images (no cache)
	$(DC) build --no-cache

up:  ## Start all services in the background
	$(DC) up -d

down:  ## Stop all services
	$(DC) down

restart:  ## Restart all services
	$(DC) restart

logs:  ## Tail logs (SERVICE=name for one service)
	$(DC) logs -f $(SERVICE)

shell:  ## Open a shell in the webserver container
	$(DC) exec webserver /bin/bash

pg-shell:  ## Open psql against the postgis container
	$(DC) exec postgis psql -U dheerajchand -d geodjango_database

status:  ## Show container status
	$(DC) ps

clean:  ## Stop services and drop volumes
	$(DC) down -v

# --- django management targets (run inside webserver container) ---

migrate:  ## Apply migrations
	$(DC) exec webserver python3 $(APP_DIR)/manage.py migrate

makemigrations:  ## Create new migrations
	$(DC) exec webserver python3 $(APP_DIR)/manage.py makemigrations

collectstatic:  ## Collect static files
	$(DC) exec webserver python3 $(APP_DIR)/manage.py collectstatic --no-input

createsuperuser:  ## Create a Django superuser
	$(DC) exec webserver python3 $(APP_DIR)/manage.py createsuperuser

test:  ## Run the Django test suite
	$(DC) exec webserver python3 $(APP_DIR)/manage.py test

# --- local (non-docker) target for downstream consumers ---

runserver:  ## Run Django locally against an existing Postgres+PostGIS
	cd $(APP_DIR) && python3 manage.py migrate && python3 manage.py runserver 0.0.0.0:8000
