from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_gis.pagination import GeoJsonPagination

# logging

import logging

logger = logging.getLogger("django")


# Create your views here.
class PlaceList(APIView):
    def get(self, request, format=None):
        logger.info("In the Place_List view")
        geo_objects = Place.objects.all().order_by("pk")
        logger.info(f"Got the queryset: {len(geo_objects)}")
        paginator = GeoJsonPagination()
        logger.info("Set the paginator")
        page = paginator.paginate_queryset(geo_objects, request)
        logger.info(f"Create a page: {page}")
        serializer = Place_Serializer(page, many=True)
        logger.info(f"Serializer created")
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, format=None):
        serializer = PlaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlaceDetail(APIView):
    def get_object(self, pk):
        try:
            return Place.objects.get(pk=pk)
        except Place.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        place = self.get_object(pk)
        serializer = PlaceSerializer(place)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        country = self.get_object(pk)
        serializer = CountrySerializer(country, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        country = self.get_object(pk)
        country.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
