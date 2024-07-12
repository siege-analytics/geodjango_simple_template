import pathlib
import importlib.util


# going to build paths for use relative to the settings file

ALL_PARENTS = list(pathlib.Path(__file__).parents)

SETTINGS_DIRECTORY = ALL_PARENTS[0]             # directory that contains the settings file
DJANGO_APP_DIRECTORY = ALL_PARENTS[1]           # directory that contains the settings directory and manage.py
DJANGO_PROJECT_DIRECTORY = ALL_PARENTS[2]       # directory that contains all django apps
DOCKER_APP_DIRECTORY = ALL_PARENTS[3]           # directory on docker that contains code

# now build paths to useful directories

# Data

DATA_DIRECTORY = DOCKER_APP_DIRECTORY / 'data'
SPATIAL_DATA_SUBDIRECTORY = DATA_DIRECTORY / 'spatial'
TABULAR_DATA_SUBDIRECTORY = DATA_DIRECTORY / 'tabular'
VECTOR_SPATIAL_DATA_SUBDIRECTORY = SPATIAL_DATA_SUBDIRECTORY / 'vector'
RASTER_SPATIAL_DATA_SUBDIRECTORY = SPATIAL_DATA_SUBDIRECTORY / 'raster'
POINTCLOUD_SPATIAL_DATA_SUBDIRECTORY = SPATIAL_DATA_SUBDIRECTORY / 'pointcloud'

# Logs

LOGS_DIRECTORY = DOCKER_APP_DIRECTORY / 'logs'


# Utilities have to be handled oddly because I'm trying to handle it with Pathlib
# and this is done with importlib

UTILITIES_PACKAGE_NAME='utilities'
PATH_TO_UTILITIES_PACKAGE=DJANGO_PROJECT_DIRECTORY / UTILITIES_PACKAGE_NAME
