from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework import generics
from django.conf import settings

# geography things
from django.contrib.gis.geos import Point

# logging

import logging

logger = logging.getLogger("django")


# Create your views here.
class Filtered_Place_List(generics.ListAPIView):

    # serializer for filtered results
    serializer_class = PlaceSerializer

    # names of variables in url

    def get_queryset(self):

        # get params from url
        # Assuming EPSG:4326
        try:
            longitude = self.request.query_params.get("longitude")
            latitude = self.request.query_params.get("latitude")
            radius = self.request.query_params.get("radius")
            epsg = self.request.query_params.get(
                "epsg", settings.DEFAULT_PROJECTION_NUMBER
            )
            reference_geom = Point((longitude, latitude), srid=epsg)
            logging.error("Made reference geom")
            # filtration
            # https://stackoverflow.com/questions/57137122/geodjango-finding-objects-in-radius
            # https://stackoverflow.com/questions/6600969/convert-between-coordinate-systems-with-geodjango
            queryset = Place.objects.filter(
                from_location__dwithin=(reference_geom, radius)
            )
        except Exception as e:
            message = ""
            message += f"There was an error getting the radius results for Place: {e}"
            logging.error(message)
            queryset = None

        return queryset
