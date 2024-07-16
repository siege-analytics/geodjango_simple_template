from rest_framework import serializers
from locations.models import Country

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['gid_0', 'geom']