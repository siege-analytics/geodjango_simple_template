from rest_framework import serializers
from locations.models import *


class Admin_Level_0Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_0
        fields = ["gid_0", "country"]


class Admin_Level_1Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_1
        fields = ["gid_1", "name_1"]


class Admin_Level_2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_2
        fields = ["gid_2", "name_2"]


class Admin_Level_3Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_3
        fields = ["gid_3", "name_3"]


class Admin_Level_4Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_4
        fields = ["gid_4", "name_4"]


class Admin_Level_5Serializer(serializers.ModelSerializer):
    class Meta:
        model = Admin_Level_5
        fields = ["gid_5", "name_5"]
