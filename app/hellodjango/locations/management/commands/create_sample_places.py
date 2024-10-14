# Imports
# Generic Python Library Imports

import sys, os
import pathlib
import csv
from os.path import split

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# custom functions and data

from locations.models import *

from utilities import *

# geography things
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import fromstr


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

        SAMPLE_LOCATIONS_CSV = (
            settings.TABULAR_DATA_SUBDIRECTORY / "az_pharmacies_geocoded.csv"
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

    United_States_Address.objects.all().delete()
    Place.objects.all().delete()

    # container for bad addresses

    bad_locations = []

    # match values for evaluation

    ROW_MATCH_VALUE = str("Match").strip()

    # open the csv and create a DictReader

    try:
        inpath = pathlib.Path(path_to_data_file)

        with inpath.open("r", newline="\n", encoding="utf-8-sig") as infile:
            reader = csv.DictReader(infile)
            for row in reader:

                if row["match"] != ROW_MATCH_VALUE:

                    message = ""
                    message += f"There was no geocode match for place {row['name']}"
                    logging.info(message)

                    continue

                else:

                    message = ""
                    message += f"There was no geocode match for place {row['name']}"
                    logging.info(message)

                    # field names
                    # name,
                    # full_address,
                    # match,
                    # match_type,
                    # reduced_address,
                    # longitude,
                    # latitude,
                    # street_side,
                    # address_check

                    # Get address fields

                    split_address_raw = row["reduced_address"].split(",")
                    split_address = list(map(str, split_address_raw))

                    street_fields = split_address[0].split(" ")
                    primary_number, street_name = (
                        street_fields[0],
                        street_fields[1:],
                    )
                    street_name = " ".join(street_name)
                    city_name = split_address[1].strip()
                    state_abbreviation = split_address[2].strip()
                    zip5 = split_address[3].strip()

                    # coordinates
                    split_coordinates = row["coordinates"].split(",")
                    longitude = split_coordinates[0].strip()
                    latitude = split_coordinates[1].strip()

                    place_address = United_States_Address(
                        primary_number=primary_number.strip(),
                        street_name=street_name.strip(),
                        city_name=city_name,
                        state_abbreviation=state_abbreviation,
                        zip5=zip5,
                        longitude=longitude,
                        latitude=latitude,
                        geom=fromstr(f"POINT({longitude} {latitude})", srid=4326),
                    )
                    #                     message = ""
                    #                     message += f"""
                    #                     pn: {primary_number}, {len(primary_number)}; sn: {street_name}, {len(street_name)}
                    #                     cn: {city_name}, {len(city_name)}; sa: {state_abbreviation}, {len(state_abbreviation)};
                    #                     z5: {zip5}, {len(zip5)}; lng: {longitude}, {len(longitude)}; lat: {latitude}, {len(latitude)}
                    # """
                    #                     logging.info(message)
                    place_address.save()
                    #
                    # get place name

                    name = row["name"]
                    if place_address:
                        new_place = Place(
                            name=name,
                            address=place_address,
                            geom=fromstr(f"POINT({longitude} {latitude})", srid=4326),
                        )
                        new_place.save()
                        message = ""
                        message += f"Place {name} created successfully."
                        logging.info(message)
                    else:
                        message = ""
                        message += (
                            f"Place {name} could not be created because of address: {place_address}"
                            f""
                        )
                        logging.info(message)

    except Exception as e:
        message = "\n"
        message += f"There was an error creating location objects: {e}"
        logger.error(message)
        return False


def geocode_addresses_with_nominatim() -> bool:
    return True
