
default: up

# enable use of SQL_ env's in make recipes
# and help keep .env up to date since includes are always prerequisites
include .env

DKC ?= docker compose

#
# Config
#

# partials to make the .env file
ENV_INCLUDES := conf/postgres.conf conf/django.conf conf/gunicorn.conf conf/build.conf

#
# Docker
#

# Helper functions
task-up = $(if $(shell $(DKC) ps -q $(1)),$(1) is running)
exec-or-run = $(if $(call task-up,$1),exec,run --rm) $1

export DOCKER_DEFAULT_PLATFORM ?= linux/amd64

confirm_amd:
	$(info DOCKER_DEFAULT_PLATFORM: $(DOCKER_DEFAULT_PLATFORM))

up down stop build : .env
	$(DKC) $@ $(if $(filter $@,up),-d)

rebuild: .env stop
	$(DKC) build --no-cache

clean: .env down
	$(DKC) rm

#
# Tasks
#

pg_term: .env
	$(DKC) $(call exec-or-run,postgis) psql -U $(SQL_USER) -d $(SQL_DATABASE)

python_term: .env
	$(DKC) $(call exec-or-run,webserver_python) /bin/bash

# Django operations

migrate collectstatic: .env
	$(DKC) $(call exec-or-run,webserver_python) python3 hellodjango/manage.py $@ --no-input

static: collectstatic

remove_migrations:
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find . -path "*/migrations/*.pyc"  -delete


.env: ${ENV_INCLUDES}
ifndef ENV_INCLUDES
	$(error ENV_INCLUDES is not set)
endif
	@# Ensure that each file ends with a newline
	@for file in $^; do \
		if [ -n "$$(tail -c 1 "$$file" | tr -d '\n')" ]; then \
			echo >> "$$file"; \
		fi; \
	done
	@ echo '# ' > $@
	@ echo '# WARNING: Generated Configuration using - $^' >> $@
	@ echo '# ' >> $@
	@cat $^ >>$@
	@echo "Generated .env using $^"
