from rest_framework import serializers
from locations.models import *


class United_States_AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = United_States_Address
        fields = "__all__"
