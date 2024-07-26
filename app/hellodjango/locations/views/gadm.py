from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from locations.models import *
from locations.serializers import *

from locations.models import Country
from locations.serializers import CountrySerializer


# Create your views here.
@csrf_exempt
def country_list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == "GET":
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = CountrySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def country_detail(request, pk):
    """
    Retrieve, update or delete a Country
    """
    # find the existing object
    try:
        country = Country.objects.get(pk=pk)
    except Country.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == "GET":
        serializer = CountrySerializer(country)
        return JsonResponse(serializer.data)

    elif request.method == "PUT":
        data = JSONParser().parse(request)
        serializer = CountrySerializer(country, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == "DELETE":
        country.delete()
        return HttpResponse(status=204)
