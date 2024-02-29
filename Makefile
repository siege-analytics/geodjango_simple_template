# Basic operations

down:
	docker-compose down

stop:
	docker compose stop

up:
	docker compose up -d

build:
	docker compose stop
	docker compose build
	docker volume create --name=geodjango_pg_data

rebuild:
	docker compose stop
	docker compose build --no-cache
	docker volume create --name=geodjango_pg_data

clean:
	docker compose down
	docker compose rm

pg_term:
	docker compose exec postgis psql -U dheerajchand -d geodjango_database

python_term:
	docker compose exec webserver_python /bin/bash

# Functional operations



