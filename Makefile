# Basic operations dev

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

# Basic operations prod

down-prod:
	docker-compose -f docker-compose.prod.yml down

stop-prod:
	docker compose -f docker-compose.prod.yml stop

up-prod:
	docker compose -f docker-compose.prod.yml up -d

build-prod:
	docker compose -f docker-compose.prod.yml stop
	docker compose -f docker-compose.prod.yml build
	docker volume create --name=geodjango_pg_data

rebuild-prod:
	docker compose -f docker-compose.prod.yml stop
	docker compose -f docker-compose.prod.yml --no-cache
	docker volume create --name=geodjango_pg_data

clean-prod:
	docker compose -f docker-compose.prod.yml down
	docker compose -f docker-compose.prod.yml rm

pg_term-prod:
	docker compose -f docker-compose.prod.yml exec postgis psql -U dheerajchand -d geodjango_database

python_term-prod:
	docker compose -f docker-compose.prod.yml exec webserver_python /bin/bash

