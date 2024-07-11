# Django functionality imports

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping

# Django models imports

from locations.models import *


DATA_TYPES_TO_PATH = {
    "VECTOR": settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY,
    "RASTER": settings.RASTER_SPATIAL_DATA_SUBDIRECTORY,
    "TABULAR": settings.TABULAR_DATA_SUBDIRECTORY,
    "POINTCLOUD": settings.POINTCLOUD_SPATIAL_DATA_SUBDIRECTORY,
}


DOWNLOADS_DISPATCHER = {
    "gadm": {
        "url": "https://geodata.ucdavis.edu/gadm/gadm4.1/gadm_410-levels.zip",
        "model_to_model": [
            {Country: country_mapping},
            {Admin_Level_1: admin_level_1_mapping},
            {Admin_Level_2: admin_level_2_mapping},
            {Admin_Level_3: admin_level_3_mapping},
            {Admin_Level_4: admin_level_4_mapping},
            {Admin_Level_5: admin_level_5_mapping},
        ],
        "type": "VECTOR",
        "unzipped_file_path": settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY
        / "gadm_410-levels"
        / "gadm_410-levels.gpkg",
    },
    "timezone": {
        "url": "https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones-with-oceans-now.shapefile.zip",
        "model_to_model": [
            {Timezone: timezone_mapping},
        ],
        "type": "VECTOR",
        "unzipped_file_path": settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY
        / "timezones-with-oceans-now.shapefile "
        / "combined-shapefile-with-oceans-now.shp",
    },
}
