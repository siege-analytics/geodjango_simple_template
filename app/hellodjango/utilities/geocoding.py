from django.conf import settings

# custom functions and data

from utilities import *
from locations.models import *
from geopy import geocoders

# logging

import logging

logger = logging.getLogger("django")


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
