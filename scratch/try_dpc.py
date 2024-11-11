from django.core.management.base import BaseCommand
from locations.models import *
from utilities import *
from django.conf import settings

# logging

import logging


logger = logging.getLogger("django")


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        # Since the CSV headers match the model fields,
        # you only need to provide the file's path (or a Python file object)

        timezones_csv = settings.TABULAR_DATA_SUBDIRECTORY / "tz.csv"

        column_to_field_mapping = {"tzid": "tzid", "geom": "geometry"}

        Timezone.objects.all().delete()
        insert_count = Timezone.objects.from_csv(
            timezones_csv,
            mapping=column_to_field_mapping,
        )

        message = ""
        message += f"{insert_count} records inserted"
        logger.info(message)
