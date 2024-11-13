from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response

# pagination

from rest_framework_gis.pagination import GeoJsonPagination


# Create your views here.

# AL0


class Admin_Level_0_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_0.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_0_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_0_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_0_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_0.objects.get(pk=pk)
        except Admin_Level_0.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al0 = self.get_object(pk)
        serializer = Admin_Level_0_Serializer(al0)
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


# AL1


class Admin_Level_1_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_1.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_1_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_1_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_1_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_1.objects.get(pk=pk)
        except Admin_Level_1.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al1 = self.get_object(pk)
        serializer = Admin_Level_1Serializer(al1)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object= self.get_object(pk)
    #     serializer = Admin_Level_1Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# AL2


class Admin_Level_2_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_2.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_2_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_2_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_2_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_2.objects.get(pk=pk)
        except Admin_Level_2.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al_object = self.get_object(pk)
        serializer = Admin_Level_2_Serializer(al_object)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object= self.get_object(pk)
    #     serializer = Admin_Level_2_Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# AL3


class Admin_Level_3_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_3.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_3_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_3_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_3_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_3.objects.get(pk=pk)
        except Admin_Level_3.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al_object = self.get_object(pk)
        serializer = Admin_Level_3_Serializer(al_object)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object= self.get_object(pk)
    #     serializer = Admin_Level_3_Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# AL4


class Admin_Level_4_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_4.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_4_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_4_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_4_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_4.objects.get(pk=pk)
        except Admin_Level_4.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al_object = self.get_object(pk)
        serializer = Admin_Level_4_Serializer(al_object)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object= self.get_object(pk)
    #     serializer = Admin_Level_4_Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


# AL5


class Admin_Level_5_List(APIView):
    def get(self, request, format=None):
        geo_objects = Admin_Level_5.objects.all().order_by("pk")

        paginator = GeoJsonPagination()

        page = paginator.paginate_queryset(geo_objects, request)

        serializer = Admin_Level_5_Serializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = Admin_Level_5_Serializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_5_Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_5.objects.get(pk=pk)
        except Admin_Level_5.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al_object = self.get_object(pk)
        serializer = Admin_Level_5_Serializer(al_object)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     al_object= self.get_object(pk)
    #     serializer = Admin_Level_5_Serializer(al_object, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     al_object = self.get_object(pk)
    #     al_object.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
