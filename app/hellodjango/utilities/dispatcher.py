# Django functionality imports

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.utils import LayerMapping

# Django models imports

from locations.models import *

# Python imports

dispatcher = {
            'gadm': {
                'url': 'http://biogeo.ucdavis.edu/data/gadm2.8/gadm28_levels.gdb.zip',
                'model_to_model': [
                    {Country: country_mapping},
                    {Admin_Level_5: admin_level_5_mapping},
                    {Admin_Level_4: admin_level_4_mapping},
                    {Admin_Level_3: admin_level_3_mapping},
                    {Admin_Level_2: admin_level_2_mapping},
                    {Admin_Level_1: admin_level_1_mapping}
                ],
                'type': 'VECTOR'
            },
            'timezone': {
                'url': 'https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones-with-oceans-now.shapefile.zip',
                'model_to_model': [
                    {Timezone: timezone_mapping},
                ],
                'type': 'VECTOR'
            },

        }