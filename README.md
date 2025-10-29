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
- [Django REST Framework][16]
- [Django REST Framework GIS Extensions][17]

# Make Live Data Available

There are currently data that are made available through Django management commands in an app called `locations`.
I should probably wrap these in `make` commands to make it easier, as you currently have to `ssh` into the
webserver container to issue them.

1. `make python_term`
2. `root@61c21188aa79:/usr/src/app# python hellodjango/manage.py fetch_and_load_standard_spatial_data`
3. `root@61c21188aa79:/usr/src/app# python hellodjango/manage.py create_sample_places`

The webserver is currently set up to run on port `8000`, so in your browser, you will need to go to:

http://127.0.0.1:8000/locations/places/

# Goals

## Currently

- Working on making all `locations` models accessible through Django REST Framework API
    - All GADM and Timezone Models work
    - Synthetic models are giving difficulty with serialization
- Adding models, fetch and load for US Census
    - Models are added, debugging mappings
    - Debugging foreign keys
- Adding geocoding API for addresses through Nominatim
- Fixing `nginx` and static files service

## Next in queue

- [Make tasks happen asynchronously][13]
- Integrate [Siege Analytics Social Warehouse][18]

## Mid-term plans

I'd like to add

- ✅ Daphne (COMPLETE - ASGI + WSGI support implemented)
- Spark
- Sedona
- GeoServer
- RabbitMQ/Django Channels
- Whitenoise / media
- ✅ Grappelli for admin (COMPLETE)

## Long-term Vision

This should be a complete spatial management tool.

# Building (Docker Images)

Building the docker images using the Makefile manages the environment variables for you. The `.env` file is
auto-generated from partial files in the `conf/` directory.

The `conf/build.conf` file is for variables that effect Docker, such as `DOCKER_DEFAULT_PLATFORM`, and
`UBUNTU_BASE_IMAGE`.

Then run `make build` to build the project.

## Build Cache

Reminder that docker uses cache to speed up builds. If system package dependencies change, you may need to rebuild
without using cache. The Makefile has a `rebuild` target that does this. (`docker compose build --no-cache`)

## Environment Config

**NB:** The docker compose `.env` file is auto-generated and git-ignored. The sources are determined by the
`ENV_INCLUDES`
env var. See the `Makefile` for more details. Changes to any of the files listed in `ENV_INCLUDES` will cause the `.env`
file to be regenerated.

If you are unsure of the status of your `.env`, you can force (always-re-make) it by running `make -B .env`.

# References:

- [TestDriven's Django on Docker][1]
- [Runitrupam's Django with Celery/Redis][5]
- [Spark on Docker][6]
- [SSL problem with pip in Docker][7]
- Pip running into SSL problems inside Docker
    - [pip.conf file][8]
    - [where to put pip.conf][9]
- [ARM64 PostGIS Image for Docker][10]
- [Adding Spatialite for dev's SQLite][11]
- [Organizing a settings.py file as a package][12]
- [Django Management Commmand options/arguments][14]
- [Useful Logging template][15]
- [Use Python to generate SHA256 Hash for Files][19]
- [PGDATA variable and path][20]
- [Removing Django migrations to start over][21]
- [Gunicorn Config File][22]
- [Adding a service in Ubuntu][23]
- [Sample Addresses For Testing Geocoder][24]
- [Get field names for a Django Model in the shell][25]
- [Correct healthcheck for PostgreSQL container][26]
- [Sample Data for Locations: Pharmacies in AZ][27]
- [GeoDjango ForeignKeys in LayerMapping][30]
- [CSS FlexBox][31]
- [Check if Django object has attributes][32]
- [GeoDjango get layers from DataSource][33]
- [Geocoding the Pharmacies][34]
- [Get Random Object][35]
- [Django REST Framework Paginator for ListAPIView][36]
- [Django Reset Primary Key for Models][37]
- [Django call management commands from inside Python][38]
- [Reset Django Migrations][39]

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

[27]:https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://www.azahcccs.gov/Resources/Downloads/PharmacyUpdates/2024/AIHPFee-For-ServicePharmacyNetwork.xlsx&ved=2ahUKEwiUkeX3x8aJAxVxw8kDHVi7EL4QFnoECBEQAQ&usg=AOvVaw1EJLz9kev_tqXZMChl15fj

[28]:https://github.com/nvm-sh/nvm

[29]:https://vite.dev/guide/

[30]:https://stackoverflow.com/questions/21197483/geodjango-layermapping-foreign-key

[31]: https://css-tricks.com/snippets/css/a-guide-to-flexbox/

[32]: https://stackoverflow.com/questions/12906933/how-to-check-if-a-model-object-has-a-given-attribute-property-field-django

[33]: https://gis.stackexchange.com/questions/413084/listing-every-layer-in-geopackage-using-fiona

[34]: https://geocoding.geo.census.gov/geocoder/locations/addressbatch?form

[35]: https://books.agiliq.com/projects/django-orm-cookbook/en/latest/random.html

[36]: https://github.com/AlisherXujanov/Fullstack-Project1/blob/0b7ea1eb103adf49c97287752bae5d1f246fb2f3/DRF.md?plain=1#L834

[37]: https://stackoverflow.com/questions/544791/django-postgresql-how-to-reset-primary-key

[38]: https://docs.djangoproject.com/en/4.0/ref/django-admin/#running-management-commands-from-your-code

[39]: https://medium.com/@mustahibmajgaonkar/how-to-reset-django-migrations-6787b2a1e723