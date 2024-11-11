from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.pagination import GeoJsonPagination
from locations.models import *


class Timezone_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Timezone
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = [
            "tzid",
        ]
