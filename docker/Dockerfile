ARG UBUNTU_BASE_IMAGE=ubuntu:24.04
FROM ${UBUNTU_BASE_IMAGE}

ARG PYTHON_VENV_PATH=/opt/venv
ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# OS packages — geospatial toolchain + Python; no PostgreSQL server daemon
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        build-essential \
        ca-certificates \
        vim \
        wget \
        curl \
        zip \
        unzip \
        python3-pip \
        python3-pyproj \
        python3-venv \
        gdal-bin \
        libgdal-dev \
        libpq-dev \
        postgis \
        netcat-openbsd \
        sqlite3 \
        spatialite-bin \
        libcairo2-dev \
        libjpeg-dev \
        libgif-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Python virtual environment
RUN python3 -m venv ${PYTHON_VENV_PATH}
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH"

# Install GDAL python bindings then project requirements
RUN pip install --upgrade pip "GDAL==$(gdal-config --version).*"

COPY requirements.txt /tmp/
RUN pip install --default-timeout=1200 -r /tmp/requirements.txt

# Non-root runtime user
RUN useradd --create-home --shell /bin/bash appuser

# Container entrypoint
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /usr/src/app
RUN chown appuser:appuser /usr/src/app
USER appuser

ENTRYPOINT ["/entrypoint.sh"]
