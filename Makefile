
default: up

include .env # enable use of SQL_ env's in make recipes

DKC ?= docker compose

#
# Config
#

TARGET_ENV ?= prod

ifeq ($(shell echo ${TARGET_ENV} | tr A-Z a-z),dev)
ENV_INCLUDES := conf/dev.env conf/django.dev.conf conf/postgres.conf
COMPOSE_SRC := docker-compose.dev.yml
else
ENV_INCLUDES := conf/prod.env conf/django.prod.conf conf/postgres.conf
COMPOSE_SRC := docker-compose.prod.yml
endif

#
# Docker
#

# Helper functions
task-up = $(if $(shell $(DKC) ps -q $(1)),$(1) is running)
exec-or-run = $(if $(call task-up,$1),exec,run --rm) $1

.env: ${ENV_INCLUDES}
	cat $^ >$@

docker-compose.yml: ${COMPOSE_SRC}
	cat $^ >$@

# this is a variable, not a command
docker-files := .env docker-compose.yml

stop:  ${docker-files}
	$(DKC) $@

down: ${docker-files}
	$(DKC) $@

up: ${docker-files}
	$(DKC) $@ -d

build: ${docker-files} stop
	$(DKC) $@


build-prod:
	TARGET_ENV=dev make -B build
	-rm -f ${docker-files}
	TARGET_ENV=prod make rebuild

rebuild: ${docker-files} stop
	$(DKC) build --no-cache

clean: ${docker-files} down
	$(DKC) rm

#
# Tasks
#

pg_term: ${docker-files}
	$(DKC) $(call exec-or-run,postgis) psql -U $(SQL_USER) -d $(SQL_DATABASE)

python_term: ${docker-files}
	$(DKC) $(call exec-or-run,webserver_python) /bin/bash

# Django operations

migrate collectstatic: ${docker-files}
	$(DKC) $(call exec-or-run,webserver_python) python3 hellodjango/manage.py $@ --no-input

static: collectstatic

