# GeoDjango Simple Template — docker image.
# Base default is ubuntu:24.04 (Python 3.12, active LTS).
# Override with `--build-arg UBUNTU_BASE_IMAGE=ubuntu:22.04` if pinned.

ARG UBUNTU_BASE_IMAGE=ubuntu:24.04
FROM ${UBUNTU_BASE_IMAGE}

ARG PYTHON_VENV_PATH=/opt/venv
ARG APP_USER=app
ARG APP_UID=10001
ARG APP_GID=10001
ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="${PYTHON_VENV_PATH}/bin:${PATH}" \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# One consolidated apt layer.
#
# Notes on package selection:
#   - libpq-dev: psycopg2 client headers (NOT the postgres server)
#   - postgis: postgis client tools (shp2pgsql, raster2pgsql); pulls libgeos
#   - sqlite3 / spatialite-bin: optional spatialite backend
#   - libcairo2-dev / libjpeg-dev / libgif-dev: pycairo, reportlab[pycairo]
#   - libgdal-dev / gdal-bin: GDAL python bindings build + runtime
#   - tzdata, ca-certificates, python3-venv: build-time prerequisites
#
# Explicitly NOT installed: postgresql / postgresql-contrib (server daemon).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tzdata \
        ca-certificates \
        build-essential \
        curl \
        wget \
        zip \
        unzip \
        python3 \
        python3-pip \
        python3-venv \
        python3-pyproj \
        gdal-bin \
        libgdal-dev \
        libpq-dev \
        postgis \
        sqlite3 \
        spatialite-bin \
        libcairo2-dev \
        libjpeg-dev \
        libgif-dev \
        netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python venv
RUN python3 -m venv "${PYTHON_VENV_PATH}"

# GDAL python bindings, pinned to the installed gdal-config version
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir "GDAL==$(gdal-config --version).*"

# Python requirements
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Non-root user
RUN groupadd --gid ${APP_GID} ${APP_USER} \
 && useradd  --uid ${APP_UID} --gid ${APP_GID} --create-home --shell /bin/bash ${APP_USER} \
 && mkdir -p /usr/src/app /home/${APP_USER}/web/staticfiles \
 && chown -R ${APP_USER}:${APP_USER} /usr/src/app /home/${APP_USER} "${PYTHON_VENV_PATH}"

# Entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /usr/src/app
USER ${APP_USER}

ENTRYPOINT ["/entrypoint.sh"]
