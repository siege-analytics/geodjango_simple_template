# python stdlib imports

import math

# django
from django.conf import settings

# custom functions and data

from utilities import *
from locations.models import *
from geopy import geocoders

# logging

import logging

logger = logging.getLogger("django")


# https://gis.stackexchange.com/questions/94645/geodjango-error-only-numeric-values-of-degree-units-are-allowed-on-geographic-d
def distance_to_decimal_degrees(distance, latitude):
    """
    Source of formulae information:
        1. https://en.wikipedia.org/wiki/Decimal_degrees
        2. http://www.movable-type.co.uk/scripts/latlong.html
    :param distance: an instance of `from django.contrib.gis.measure.Distance`
    :param latitude: y - coordinate of a point/location
    """
    lat_radians = latitude * (math.pi / 180)
    # 1 longitudinal degree at the equator equal 111,319.5m equiv to 111.32km
    return distance.m / (111_319.5 * math.cos(lat_radians))


def geocode_with_nominatim_public(concatenated_address: str) -> str:

    try:
        geocoder = geocoders.Nominatim(user_agent=settings.NOMINATIM_USER_AGENT)
        location = geocoder.geocode(concatenated_address)

        result = geocoder.geocode(concatenated_address, addressdetails=True)

        address_information = result.raw

        message = ""
        message += f"Successfully geocoded {concatenated_address}"
        logging.info(message)

        return address_information

    except Exception as e:
        message = ""
        message += f"There was an error geocoding {concatenated_address}: {e}"
        logging.error(message)

        return False
