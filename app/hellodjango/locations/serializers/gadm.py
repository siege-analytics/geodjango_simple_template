from rest_framework_gis.serializers import GeoFeatureModelSerializer
from locations.models import *


class Admin_Level_0_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_0
        geo_field = "geom"
        fields = ["gid_0", "country"]


class Admin_Level_1_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_1
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = ["gid_1", "name_1"]


class Admin_Level_2_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_2
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = ["gid_2", "name_2"]


class Admin_Level_3_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_3
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = ["gid_3", "name_3"]


class Admin_Level_4_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_4
        geo_field = "geom"
        pagination_class = GeoJsonPagination
        fields = ["gid_4", "name_4"]


class Admin_Level_5_Serializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin_Level_5
        pagination_class = GeoJsonPagination
        geo_field = "geom"
        fields = ["gid_5", "name_5"]
