# Imports
import pathlib

#Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Generic Python Library Imports

import sys, os
import importlib.util

# custom functions and data

#from utilities.file_utilities import *
from utilities import *

# Useful Constants

# BOUNDARIES_URL = 'https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones-with-oceans-now.shapefile.zip'



class Command(BaseCommand):
    args = ''
    help = 'Fetches data specified by CLI argument, data must be in the dispatcher'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='*')

    def handle(self, *args, **kwargs):

        # get command line specified options
        model_set = kwargs['models']
        known_models = list(dispatcher.keys())

        # specify which models to work on
        # if the user specifies nothing, do them all

        if len(model_set) == 0:
            models_to_work_on = known_models
        else:
            models_to_work_on = [m for m in model_set if m.lower() in known_models]
            models_that_cannot_be_worked_on = [m for m in model_set if not m.lower() in known_models]

        print(models_that_cannot_be_worked_on)
        print(models_to_work_on)

        # start work

        for m in models_to_work_on:
            m = m.lower()


        self.success = True


        # Output mesages

        if self.success == True:
            self.stdout.write('Successfully fetched the boundaries for data.')


def fetch_and_load_all_data(model_to_work_on):
    message = f"Working on {model_to_work_on}"
    print(message)

    params = dispatcher[m]

    url = params['url']
    data_type = params['data_type']
