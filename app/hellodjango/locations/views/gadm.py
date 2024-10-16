from locations.models import *
from locations.serializers import *

from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response


# Create your views here.
class CountryList(APIView):
    def get(self, request, format=None):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)

    # This method is hypothetical because we will never add data
    # def post(self, request, format=None):
    #     serializer = CountrySerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryDetail(APIView):
    def get_object(self, pk):
        try:
            return Country.objects.get(pk=pk)
        except Country.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        country = self.get_object(pk)
        serializer = CountrySerializer(country)
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
