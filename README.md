# GeoDjango Simple Template

A production-ready template for building GeoDjango applications with spatial data support, REST APIs, and real-time capabilities.

## Tech Stack

### Core Components
- **Django 5.2** with GeoDjango
- **Daphne** - ASGI server (supports WSGI + WebSockets)
- **PostGIS** - Spatial database
- **nginx** - Reverse proxy
- **Django REST Framework** + GIS extensions
- **Grappelli** - Enhanced Django admin

### Frontend (Optional)
- **Vue 3** + Vite
- **NVM** for Node.js version management

## Quick Start

```bash
# Build and start all services
make build
make up

# Access the application
# Django API:  http://localhost:8000/locations/places/
# Nginx:       http://localhost:8001
# Admin:       http://localhost:8000/admin/
# PostGIS:     localhost:54322
```

## Load Sample Data

```bash
# Shell into webserver container
make shell

# Load standard spatial data (GADM, timezones)
python hellodjango/manage.py fetch_and_load_standard_spatial_data

# Create sample places
python hellodjango/manage.py create_sample_places

# Load Census TIGER data
python hellodjango/manage.py fetch_and_load_census_tiger_data
```

## Celery (Idiot‑Proof Guide)

Use Celery workers to split big/slow tasks across multiple containers so the web app stays fast.

### 1) Start everything

```bash
make build
make up

# You should see these services running:
# - geodjango_webserver (Daphne)
# - geodjango_postgis (PostGIS)
# - geodjango_redis (Redis)
# - geodjango_celery_1, geodjango_celery_2, geodjango_celery_3 (Celery workers)
```

### 2) Run heavy commands ASYNC (don’t block your terminal)

```bash
make shell

# Load spatial data in the background (parallelized across 3 workers)
python hellodjango/manage.py fetch_and_load_standard_spatial_data --async

# Load Census TIGER data in the background
python hellodjango/manage.py fetch_and_load_census_tiger_data --async

# Create sample data in the background
python hellodjango/manage.py create_sample_places --async
```

You’ll get back a Task ID immediately. Work happens on the workers.

### 3) How to tell if workers are alive

```bash
# See workers listed
docker ps | grep geodjango_celery

# See a worker become ready
docker logs geodjango_celery_1 | grep ready

# Inspect workers (registered tasks, stats)
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect stats
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect registered
```

### 4) Watch task progress (no UI)

```bash
# Stream logs from all workers in separate terminals
docker logs -f geodjango_celery_1
docker logs -f geodjango_celery_2
docker logs -f geodjango_celery_3

# See currently running tasks
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect active
```

### 5) Submit tasks from Python (advanced, still idiot‑proof)

```python
from locations.tasks import fetch_and_load_standard_spatial_data_async

result = fetch_and_load_standard_spatial_data_async.delay(['gadm', 'timezone'])
print(result.id)      # Task ID
print(result.status)  # PENDING → STARTED → SUCCESS/FAILURE

# (Optional) wait for result (blocks)
result.get(timeout=900)
```

### 6) Optional: Web UI with Flower

Flower gives you a dashboard to see tasks, states, and workers.

Steps:
- Flower is included as a service; just bring the stack up.
- Open Flower: http://localhost:5555

What you’ll see:
- Workers online/offline
- Task list with live states
- Per‑task details, retries, errors

If the UI isn’t reachable, run:

```bash
make up
docker logs -f geodjango_flower
```

### FAQ

- "It looks stuck." → Check `docker logs -f geodjango_celery_1` for progress. Big downloads/unzips take time.
- "I want to use all workers." → You already are. Tasks are split automatically.
- "How do I retry?" → Re‑run the manage.py command with `--async`. Failed tasks are independent.

## API Endpoints

- `/locations/places/` - GeoJSON places API
- `/locations/admin_level_0s/` - Country-level admin boundaries
- `/locations/admin_level_1s/` - State/province-level
- `/locations/timezones/` - Timezone data
- `/admin/` - Django admin interface

## Features

### ✅ Complete
- Daphne ASGI server (WSGI + WebSocket support)
- PostGIS spatial database
- Django REST Framework with GIS extensions
- Grappelli enhanced admin interface
- GADM administrative boundaries (global)
- Timezone data
- US Census TIGER data support
- Geocoding via Nominatim
- nginx with static file serving

### 🔄 In Progress
- Synthetic location models refinement
- Additional US Census data integration

### 📋 Planned
- Django Channels (WebSocket support)
- Apache Spark integration
- Apache Sedona (geospatial Spark)
- GeoServer for tile serving
- RabbitMQ for task queue
- Whitenoise for media files

## Makefile Commands

```bash
make build          # Build all Docker images
make up             # Start all services
make down           # Stop all services
make restart        # Restart all services
make logs           # Show logs (add SERVICE=webserver for specific service)
make shell          # Open shell in webserver container
make pg-shell       # Open PostgreSQL shell
make migrate        # Run Django migrations
make collectstatic  # Collect static files
make clean          # Remove containers and volumes
```

## Building

```bash
# First time setup
make build
make up
make migrate
make collectstatic

# Load sample data (optional)
make shell
python hellodjango/manage.py fetch_and_load_standard_spatial_data
python hellodjango/manage.py create_sample_places
```

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