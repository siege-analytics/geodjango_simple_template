from rest_framework import serializers
from locations.models import *
from .addresses import United_States_AddressSerializer


class PlaceSerializer(serializers.ModelSerializer):

    address = United_States_AddressSerializer(many=False, read_only=True)

    class Meta:
        model = Place
        fields = "__all__"
        depth = 1


class LocalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Locality
        fields = "__all__"
