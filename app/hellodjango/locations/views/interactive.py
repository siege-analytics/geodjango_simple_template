import locations.models
import locations.serializers

from django.http import Http404
from rest_framework import generics

from app.hellodjango.hellodjango.settings import DEFAULT_PROJECTION_FROM_COORDINATES_IN_WKT


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
        epsg = self.request.query_params.get("epsg", DEFAULT_PROJECTION_FROM_COORDINATES_IN_WKT)

        reference_geom = Point(longitude, latitude)

        # filtration

        # queryset = locations.models.Place.objects.filter()

        return queryset
