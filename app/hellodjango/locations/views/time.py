from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_gis.pagination import GeoJsonPagination

import logging

logger = logging.getLogger("django")

# Create your views here.


# Timezone


class Timezone_List(APIView):
    def get(self, request, format=None):

        geo_objects = Timezone.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Timezone_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

        # return Response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_0_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Timezone_Detail(APIView):
    def get_object(self, pk):
        try:
            return Timezone.objects.get(pk=pk)
        except Timezone.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        geo_object = self.get_object(pk)
        serializer = Timezone_Serializer(geo_object)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     serializer = Admin_Level_0_Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
