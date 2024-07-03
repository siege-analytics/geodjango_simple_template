# Imports
import pathlib

#Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Generic Python Library Imports

import sys, os
import importlib.util

# custom functions

from utilities.file_utilities import *

# Useful Constants

BOUNDARIES_URL = 'https://github.com/evansiroky/timezone-boundary-builder/releases/download/2024a/timezones-with-oceans-now.shapefile.zip'



class Command(BaseCommand):
    args = ''
    help = 'Fetches data specified by CLI argument, data must be in the dispatcher'

    def handle(self, *args, **options):
        try:
            local_filename = generate_local_path_from_url(
                url=BOUNDARIES_URL,
                directory_path=settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY,
            )

            downloaded_file = download_file(
                url=BOUNDARIES_URL,
                local_filename=str(local_filename)
            )

            path_to_downloaded_file = pathlib.Path(downloaded_file)
            unzipped_downloaded_file = unzip_file_to_its_own_directory(
                path_to_zipfile=path_to_downloaded_file,
                new_dir_name=None,
                new_dir_parent=None
            )

        except Exception as ex:
            raise CommandError("There was an error at the command level: %s" % (ex))
            sys.exit()

        self.success = True

        # Output mesages

        if self.success == True:
            self.stdout.write('Successfully fetched the boundaries for Natural Earth Timezone boundaries.')

