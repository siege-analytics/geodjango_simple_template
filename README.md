# GeoDjango Template

This repository contains a simple template for building GeoDjango applications. I wrote it to make life easier for people trying to make simple applications, borrowing from [this project][1].

It currently supports two environments

- Dev
- Prod

The `Makefile` has parallel commands for most things relating to building the project. Default commands relate to the `dev` environment, `prod` commands have a flag on them.
It's a good idea to use the Makefile.

The project makes use of some standard technologies:

- [gunicorn][2]
- [nginx][3]
- [PostGIS][4]

Currently debugging `nginx`.

# Goals

I'd like to add

- Spark
- Sedona
- GeoServer

[1]: https://testdriven.io/blog/dockerizing-django-with-postgres-gunicorn-and-nginx/?utm_source=pocket_saves
[2]: https://gunicorn.org
[3]: https://www.nginx.com
[4]: https://www.postgis.net


