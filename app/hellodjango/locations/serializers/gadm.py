from rest_framework import serializers
from locations.models import *


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class Admin_Level_1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_1
        fields = "__all__"


class Admin_Level_2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_2
        fields = "__all__"


class Admin_Level_3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_3
        fields = "__all__"


class Admin_Level_4Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_4
        fields = "__all__"


class Admin_Level_5Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_5
        fields = "__all__"
