# Imports
# Generic Python Library Imports

import sys, os
import pathlib
import csv

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# custom functions and data

from locations.models import *

try:
    from utilities import *

    print("Successfully imported utilities")
except Exception as e:
    print(f"Failed to import utilities:{e}")

# logging

import logging

logger = logging.getLogger("django")


class Command(BaseCommand):
    args = ""
    help = "Creates Location objects from AZ government data and uses the Nominatim API to geocode them"

    def handle(self, *args, **kwargs):

        # get command line specified options
        # container variables

        successes = []
        failures = []

        # specify which models to work on
        # if the user specifies nothing, do them all

        SAMPLE_LOCATIONS_CSV = (
            settings.TABULAR_DATA_SUBDIRECTORY / "list_of_pharmacies_in_az.csv"
        )

        # start work
        try:
            message = "\n"
            message += "About to do the business"

            result = create_places_from_data_file(
                path_to_data_file=SAMPLE_LOCATIONS_CSV
            )

            successes.append(result)
        except Exception as e:
            message = "\n"
            message += f"There was an error at the management command level working on {message}: {e}"
            logger.error(message)
            failures.append(message)

        # count failures
        if len(failures) > 0:
            message = "\n FAILURE"
            message += f"\n The following models succeeded : {successes}"
            message += f"\n The following models failed : {failures}"

            logger.error(message)

        else:
            message = "\n SUCCESS"
            message += f"\n The following models succeeded : {successes}"
            message += f"\n The following models failed : {failures}"

            logger.info(message)


def create_places_from_data_file(path_to_data_file: pathlib.Path) -> bool:

    # container for bad addresses

    bad_locations = []

    # open the csv and create a DictReader

    try:
        inpath = pathlib.Path(path_to_data_file)

        with inpath.open("r", newline="\n", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:

                # field names
                # PHARMACY_NAME
                # PHARMACY_ADDRESS
                # CITY
                # STATE
                # ZIP_CODE
                # PHONE_NUMBER

                # Get address fields

                split_address_raw = row["PHARMACY_ADDRESS"].split(" ")
                split_address = list(map(str, split_address_raw))

                primary_number, street_name_list = split_address[0], split_address[1:]
                street_name = " ".join(street_name_list)
                city_name = row["CITY"]
                state_abbreviation = row["STATE"]
                zip5 = row["ZIP_CODE"]

                place_address = create_united_states_address(
                    primary_number=primary_number,
                    street_name=street_name,
                    city_name=city_name,
                    state_abbreviation=state_abbreviation,
                    zip5=zip5,
                )
                #
                # get place name

                name = row["PHARMACY_NAME"]

                new_place = Place(name=name, address=place_address)
                new_place.save()
        #
        # message = "\n"
        # message += "Success creating location objects"
        # logger.info(message)
        # return True

    except Exception as e:
        message = "\n"
        message += f"There was an error creating location objects: {e}"
        logger.error(message)
        return False


def geocode_addresses_with_nominatim() -> bool:
    return True
