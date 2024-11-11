from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.pagination import GeoJsonPagination
from locations.models import *


class Timezone_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_0
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = [
            "tzid",
        ]
