# Imports
import pathlib
import csv

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Generic Python Library Imports

import sys, os
# custom functions and data

# from utilities.file_utilities import *
from utilities import *

# logging

import logging
logger = logging.getLogger("django")

class Command(BaseCommand):
    args = ""
    help = "Creates US Address objects from Crime data and uses the Nominatim API to geocode them"

    def handle(self, *args, **kwargs):

        # get command line specified options
        # container variables

        successes = []
        failures = []

        # specify which models to work on
        # if the user specifies nothing, do them all

        CHICAGO_CRIMES_GEO_CSV = settings.TABULAR_DATA_SUBDIRECTORY / 'Crime.csv'

        # start work
        try:
            message="\n"
            message+="Hello Cupcake"

            result=create_addresses_from_data_file(path_to_data_file=CHICAGO_CRIMES_GEO_CSV)

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


def create_addresses_from_data_file(path_to_data_file: pathlib.Path)->bool:

    # container for bad addresses

    bad_addresses = []

    # open the csv and create a DictReader

    inpath = pathlib.Path(path_to_data_file)

    with inpath.open("r", newline="\n", encoding="utf-8-sig") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            logger.info(row)

    return True





