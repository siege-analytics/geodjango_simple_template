# Args from compose
ARG UBUNTU_BASE_IMAGE=ubuntu:latest
ARG PYTHON_VENV_PATH=/opt/venv

FROM ${UBUNTU_BASE_IMAGE}

# Environmental Variables
ENV DEBIAN_FRONTEND noninteractive
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install the basics
RUN apt-get update
RUN apt-get install -y tzdata
RUN apt-get clean && apt-get install -y \
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
    postgresql \
    postgresql-contrib \
    postgis \
    netcat-traditional

# Activate Python Virtual Environment

ENV PYTHON_VENV_PATH=${PYTHON_VENV_PATH}
RUN python3 -m venv ${PYTHON_VENV_PATH}
ENV PATH="${PYTHON_VENV_PATH}/bin:$PATH"

# Install GDAL python bindings
RUN apt-get install -y --install-recommends libgdal-dev
RUN export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
export C_INCLUDE_PATH=/usr/include/gdal && \
pip install GDAL=="$(gdal-config --version).*"

# Install PIP requirements
ADD requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt

# copy code over

# set work directory
WORKDIR /usr/src/app

COPY . .
# COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

