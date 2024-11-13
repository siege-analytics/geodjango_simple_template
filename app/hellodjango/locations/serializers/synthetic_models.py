from rest_framework import serializers
from locations.models import *
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .addresses import United_States_AddressSerializer


class Place_Serializer(GeoFeatureModelSerializer):

    address = United_States_AddressSerializer(many=False, read_only=True)

    class Meta:
        model = Place
        geo_field = "geom"
        fields = "__all__"
        depth = 1


class LocalitySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Locality
        geo_field = "geom"
        fields = "__all__"
