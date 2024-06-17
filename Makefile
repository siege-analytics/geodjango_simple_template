# Basic operations dev

default: build

link-dev:
	ln -sf .env.dev .env

down:
	docker compose down

stop:
	docker compose stop

up: .env
	docker compose up -d

build: .env
	make link-dev
	docker compose stop
	docker compose build
	docker volume create --name=geodjango_pg_data

rebuild:
	make link-dev
	docker compose stop
	docker compose build --no-cache
	docker volume create --name=geodjango_pg_data

clean:
	docker compose down
	docker compose rm

# Helper functions
task-up = $(if $(shell $(DKC) ps -q $(1)),$(1) is running)
exec-or-run = $(if $(call task-up,$1),exec,run --rm) $1

pg_term:
	docker compose $(call exec-or-run,postgis) psql -U dheerajchand -d geodjango_database

python_term:
	docker compose $(call exec-or-run,webserver_python) /bin/bash

# Basic operations prod

link-prod:
	ln -sf .env.prod .env

down-prod:
	docker-compose -f docker-compose.prod.yml down

stop-prod:
	docker compose -f docker-compose.prod.yml stop

up-prod:
	docker compose -f docker-compose.prod.yml up -d

build-prod:
	make link-prod
	docker compose -f docker-compose.prod.yml stop
	docker compose -f docker-compose.prod.yml build
	docker volume create --name=geodjango_pg_data

rebuild-prod:
	make link-prod
	docker compose -f docker-compose.prod.yml stop
	docker compose -f docker-compose.prod.yml build --no-cache
	docker volume create --name=geodjango_pg_data

clean-prod:
	docker compose -f docker-compose.prod.yml down
	docker compose -f docker-compose.prod.yml rm

pg_term-prod:
	docker compose -f docker-compose.prod.yml exec postgis psql -U dheerajchand -d geodjango_database

python_term-prod:
	docker compose -f docker-compose.prod.yml exec webserver_python /bin/bash

# Django operations dev

migrate:

	docker compose exec webserver_python python3 hellodjango/manage.py migrate --no-input

static:

	docker compose exec webserver_python python3 hellodjango/manage.py collectstatic --no-input

# Django operations prod

migrate-prod:

	docker compose -f docker-compose.prod.yml exec webserver_python python3 hellodjango/manage.py migrate --no-input

static:

	docker compose -f docker-compose.prod.yml exec webserver_python python3 hellodjango/manage.py collectstatic --no-input
