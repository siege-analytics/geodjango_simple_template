from rest_framework import serializers
from locations.models import *

from rest_framework_gis.pagination import GeoJsonPagination


class United_States_AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = United_States_Address
        pagination_class = GeoJsonPagination
        fields = "__all__"
