from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class Admin_Level_0List(APIView):
    def get(self, request, format=None):
        al0s = Admin_Level_0.objects.all()
        serializer = Admin_Level_0Serializer(al0s, many=True)
        return Response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = CountrySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_0Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_0.objects.get(pk=pk)
        except Admin_Level_0.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al0 = self.get_object(pk)
        serializer = Admin_Level_0Serializer(al0)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     country = self.get_object(pk)
    #     serializer = CountrySerializer(country, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     country = self.get_object(pk)
    #     country.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class Admin_Level_1List(APIView):
    def get(self, request, format=None):
        al0s = Admin_Level_1.objects.all()
        serializer = Admin_Level_1Serializer(al0s, many=True)
        return Response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = CountrySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Admin_Level_1Detail(APIView):
    def get_object(self, pk):
        try:
            return Admin_Level_1.objects.get(pk=pk)
        except Admin_Level_1.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        al0 = self.get_object(pk)
        serializer = Admin_Level_1Serializer(al0)
        return Response(serializer.data)

    # these methods are hypothetical

    # def put(self, request, pk, format=None):
    #     country = self.get_object(pk)
    #     serializer = CountrySerializer(country, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    #
    # def delete(self, request, pk, format=None):
    #     country = self.get_object(pk)
    #     country.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)
