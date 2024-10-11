from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework import generics
from django.conf import settings


# Create your views here.
class Filtered_Place_List(generics.ListAPIView):

    # serializer for filtered results
    serializer_class = PlaceSerializer

    # names of variables in url

    def get_queryset(self):

        # get params from url
        # Assuming EPSG:4326

        longitude = self.request.query_params.get("longitude")
        latitude = self.request.query_params.get("latitude")
        radius = self.request.query_params.get("radius")
        epsg = self.request.query_params.get("epsg", settings.DEFAULT_PROJECTION_NUMBER)
        reference_geom = Point(longitude, latitude, epsg)

        # filtration
        # https://stackoverflow.com/questions/57137122/geodjango-finding-objects-in-radius
        # https://stackoverflow.com/questions/6600969/convert-between-coordinate-systems-with-geodjango
        # queryset = locations.models.Place.objects.filter()

        return queryset
