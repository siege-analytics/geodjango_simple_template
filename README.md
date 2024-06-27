# GeoDjango Template

This repository contains a simple template for building GeoDjango applications. I wrote it to make life easier for people trying to make simple applications, borrowing from [this project][1].

It currently supports two environments

- Dev (default)
- Prod

The `Makefile` has parallel commands for most things relating to building the project. Default commands relate to the `dev` environment, `prod` commands have a flag on them.
It's a good idea to use the Makefile.

The project makes use of some standard technologies:

- [gunicorn][2]
- [nginx][3]
- [PostGIS][4]

Currently adding `redis`.

# Building

The `TARGET_ENV` env variable determines the environment to build. The default is `dev`. To build the project for production, set `TARGET_ENV=prod` (case in-sensitive). **You should delete the `docker-compose.yml` and `.env` files before switching environments.**

Override UBUNTU_BASE_IMAGE in the `.env` file to use a different base image, e.g. `UBUNTU_BASE_IMAGE=arm64v8/ubuntu:latest`.

Then run `make build` to build the project.

## Production Builds

**NB:** The production image uses the Dev image as its base. Be sure to build the Dev image first.

The Makefile has a `build-prod` target that builds the dev image, and deletes the docker files in-between switching environments.

## Environment Config

**NB:** The docker compose files (`docker-compose.yml`, `.env`) are auto-generated and git-ignored. The sources are determined by the `TARGET_ENV` env var. See the `Makefile` for more details.

The `conf/` directory contains ingredients for the auto-generated `.env` file. The `Makefile` declares `ENV_INCLUDES` depending on the value of `TARGET_ENV`. The `dev.env` and `prod.env` files are meant for general environment config. Other files are meant for specific services, e.g. django and postgres.

# Goals

I'd like to add

- Daphne
- Spark
- Sedona
- GeoServer
- Redis/Django Channels

# References:

- [TestDriven's Django on Docker][1]
- [Runitrupam's Django with Celery/Redis][5]
- [Spark on Docker][6]
- [SSL problem with pip in Docker](7)
- Pip running into SSL problems inside Docker
  - [pip.conf file](8)
  - [where to put pip.conf](9)
- [ARM64 PostGIS Image for Docker](10)

[1]: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/?utm_source=pocket_saves
[2]: https://gunicorn.org
[3]: https://www.nginx.com
[4]: https://www.postgis.net
[5]: https://github.com/runitrupam/Django-Docker-Compose-Celery-Redis-PostgreSQL
[6]: https://medium.com/@SaphE/testing-apache-spark-locally-docker-compose-and-kubernetes-deployment-94d35a54f222
[7]: https://stackoverflow.com/questions/25981703/pip-install-fails-with-connection-error-ssl-certificate-verify-failed-certi/73745221
[8]: https://stackoverflow.com/questions/59287824/specifying-multiple-trusted-hosts-in-pip-conf
[9]: https://stackoverflow.com/questions/38869231/python-cant-find-the-file-pip-conf
[10]: https://github.com/Tob1as/docker-postgresql-postgis