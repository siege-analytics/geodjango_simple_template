# GeoDjango Template

This repository contains a simple template for building GeoDjango applications. I wrote it to make life easier for
people trying to make simple applications, borrowing from [this project][1].

It currently supports two environments

- Dev (default)
- Prod

The `Makefile` has parallel commands for most things relating to building the project. Default commands relate to
the `dev` environment, `prod` commands have a flag on them.
It's a good idea to use the Makefile.

The project makes use of some standard technologies:

- [gunicorn][2]
- [nginx][3]
- [PostGIS][4]
- [NVM][28]
- [Vue/Vite][29]

# Currently

Adding a Django application to import and convert vector and raster data formats using OGR/GDAL and Django Rest
Framework.

# Immediately to do

- [Make tasks happen asynchronously](13)
- Add Django REST Framework
    - [Django REST Framework](16)
    - [Django REST Framework GIS Extensions](17)
- Integrate [Siege Analytics Social Warehouse](18)

# Building

The `TARGET_ENV` env variable determines the environment to build. The default is `dev`. To build the project for
production, set `TARGET_ENV=prod` (case in-sensitive). **You should delete the `docker-compose.yml` and `.env` files
before switching environments.**

Override UBUNTU_BASE_IMAGE in the `.env` file to use a different base image,
e.g. `UBUNTU_BASE_IMAGE=arm64v8/ubuntu:latest`.

Then run `make build` to build the project.

## Production Builds

The Makefile has a `build-prod` target that does a `--no-cache` build. It automatically switches the `TARGET_ENV`
to `prod` to load the `*prod.env` files.

## Environment Config

**NB:** The docker compose `.env` file is auto-generated and git-ignored. The sources are determined by the `TARGET_ENV`
env var. See the `Makefile` for more details.

The `conf/` directory contains ingredients for the auto-generated `.env` file. The `Makefile` declares `ENV_INCLUDES`
depending on the value of `TARGET_ENV`. The `dev.env` and `prod.env` files are meant for general environment config.
Other files are meant for specific services, e.g. django and postgres.

# Goals

I'd like to add

- Daphne
- Spark
- Sedona
- GeoServer
- RabbitMQ/Django Channels

# References:

- [TestDriven's Django on Docker][1]
- [Runitrupam's Django with Celery/Redis][5]
- [Spark on Docker][6]
- [SSL problem with pip in Docker](7)
- Pip running into SSL problems inside Docker
    - [pip.conf file](8)
    - [where to put pip.conf](9)
- [ARM64 PostGIS Image for Docker](10)
- [Adding Spatialite for dev's SQLite](11)
- [Organizing a settings.py file as a package](12)
- [Django Management Commmand options/arguments](14)
- [Useful Logging template](15)
- [Use Python to generate SHA256 Hash for Files](19)
- [PGDATA variable and path](20)
- [Removing Django migrations to start over](21)
- [Gunicorn Config File](22)
- [Adding a service in Ubuntu](23)
- [Sample Addresses For Testing Geocoder](24)
- [Get field names for a Django Model in the shell](25)
- [Correct healthcheck for PostgreSQL container](26)
- [Sample Data for Locations: Pharmacies in AZ](27)
- [GeoDjango ForeignKeys in LayerMapping](30)
- [CSS FlexBox](31)
- [Check if Django object has attributes](32)

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

[11]: https://zoomadmin.com/HowToInstall/UbuntuPackage/spatialite-bin

[12]: https://www.reddit.com/r/django/comments/l9s3r4/how_do_you_organize_your_settingspy_file_to_keep/

[13]: https://pub.aimind.so/download-large-file-in-python-with-beautiful-progress-bar-f4f86b394ad7

[14]: https://simpleisbetterthancomplex.com/tutorial/2018/08/27/how-to-create-custom-django-management-commands.html

[15]: https://www.crowdstrike.com/guides/python-logging/logging-with-django/

[16]: https://www.django-rest-framework.org

[17]: https://github.com/openwisp/django-rest-framework-gis

[18]: https://github.com/siege-analytics/socialwarehouse

[19]: https://gist.github.com/jakekara/078899caaf8d5e6c74ef58d16ce7e703

[20]: https://www.postgresql.org/docs/16/storage-file-layout.html

[21]: https://simpleisbetterthancomplex.com/tutorial/2016/07/26/how-to-reset-migrations.html

[22]: https://stackoverflow.com/questions/12063463/where-is-the-gunicorn-config-file

[23]: https://superuser.com/questions/1839901/how-to-properly-create-a-service-in-ubuntu

[24]:https://github.com/geocommons/geocoder/blob/master/test/data/address-sample.csv

[25]:https://stackoverflow.com/questions/3647805/how-to-get-all-fields-for-a-django-model

[26]:https://github.com/peter-evans/docker-compose-healthcheck/issues/16

[27]:https://www.azahcccs.gov/Resources/Downloads/PharmacyUpdates/AIHPFee-For-ServicePharmacyNetwork.pdf

[28]:https://github.com/nvm-sh/nvm

[29]:https://vite.dev/guide/

[30]:https://stackoverflow.com/questions/21197483/geodjango-layermapping-foreign-key

[31]: https://css-tricks.com/snippets/css/a-guide-to-flexbox/

[32]: https://stackoverflow.com/questions/12906933/how-to-check-if-a-model-object-has-a-given-attribute-property-field-django
