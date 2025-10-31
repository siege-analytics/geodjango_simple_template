# Imports
import pathlib
import importlib

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.contrib.gis.utils import LayerMapping

# geospatial libraries

import geopandas as gpd

# python libraries

import numpy as np

# Generic Python Library Imports

import sys, os

# custom functions and data

from utilities import *

# logging

import logging

logger = logging.getLogger("django")


class Command(BaseCommand):
    args = ""
    help = "Fetches data specified by CLI argument, data must be in the dispatcher"

    def add_arguments(self, parser):
        parser.add_argument("models", nargs="*")
        parser.add_argument(
            '--async',
            action='store_true',
            help='Run as Celery task (async)',
        )
        parser.add_argument(
            '--optimized',
            action='store_true',
            help='Use optimized per-layer parallel loading (GADM only)',
        )
        parser.add_argument(
            '--pipelined',
            action='store_true',
            help='Use pipelined approach: preprocess→load per worker, all parallel (GADM only)',
        )
        parser.add_argument(
            '--sedonadb',
            action='store_true',
            help='Use SedonaDB (Arrow-based) for preprocessing - FASTEST option (GADM only)',
        )

    def handle(self, *args, **kwargs):
        # Check if async flag is set
        use_async = kwargs.get('async', False)
        use_optimized = kwargs.get('optimized', False)
        use_pipelined = kwargs.get('pipelined', False)
        use_sedonadb = kwargs.get('sedonadb', False)
        models = kwargs.get("models")
        
        if use_async:
            # Check for SedonaDB GADM loading (FASTEST option)
            if use_sedonadb and models and 'gadm' in models:
                from locations.tasks_sedonadb import load_gadm_sedonadb
                result = load_gadm_sedonadb.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ SedonaDB GADM load queued: {result.id}')
                )
                self.stdout.write('Engine: SedonaDB (Arrow + DataFusion)')
                self.stdout.write('Pipeline: 6 parallel SedonaDB preprocess → load → FK population')
                self.stdout.write('Expected time: ~5-8 minutes (vs 25+ sequential)')
                self.stdout.write(f'Monitor: docker logs geodjango_celery_1 geodjango_celery_2 geodjango_celery_3 -f')
                return
            
            # Check for pipelined GADM loading (GOOD option)
            if use_pipelined and models and 'gadm' in models:
                from locations.tasks_gadm_pipeline import load_gadm_pipelined
                result = load_gadm_pipelined.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Pipelined GADM load queued: {result.id}')
                )
                self.stdout.write('Pipeline: Each worker does preprocess→load (×2 layers), all parallel')
                self.stdout.write('Expected time: ~8-10 minutes (vs 25+ sequential)')
                self.stdout.write(f'Monitor: docker logs geodjango_celery_1 geodjango_celery_2 geodjango_celery_3 -f')
                return
            
            # Check for optimized GADM loading
            if use_optimized and models and 'gadm' in models:
                from locations.tasks_gadm_optimized import load_gadm_parallel_optimized
                result = load_gadm_parallel_optimized.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Optimized GADM load queued: {result.id}')
                )
                self.stdout.write('This will: 6 parallel layer loads → FK population')
                self.stdout.write('Expected time: ~8-10 minutes (vs 25+ sequential)')
                self.stdout.write(f'Monitor: docker logs geodjango_celery_1 geodjango_celery_2 geodjango_celery_3 -f')
                return
            
            # Standard async (current behavior)
            from locations.tasks import fetch_and_load_standard_spatial_data_async
            result = fetch_and_load_standard_spatial_data_async.delay(models)
            self.stdout.write(
                self.style.SUCCESS(f'✅ Task queued: {result.id}')
            )
            self.stdout.write(f'Monitor progress: docker logs geodjango_celery_1 -f')
            return
        
        # get command line specified options
        model_set = kwargs["models"]
        known_models = list(DOWNLOADS_DISPATCHER.keys())

        # container variables
        models_to_work_on = []
        models_that_cannot_be_worked_on = []
        successes = []
        failures = []

        # specify which models to work on
        # if the user specifies nothing, do them all

        if len(model_set) == 0:
            models_to_work_on = known_models
        else:
            models_to_work_on = [m for m in model_set if m.lower() in known_models]
            models_that_cannot_be_worked_on = [
                m for m in model_set if not m.lower() in known_models
            ]

        logger.info(models_that_cannot_be_worked_on)
        logger.info(models_to_work_on)

        # start work
        try:
            for m in models_to_work_on:
                m = m.lower()
                fetch_and_load_all_data(m)
                successes.append(m)
        except Exception as e:
            message = "\n"
            message += f"There was an error at the management command level working on {m}: {e}"
            logger.error(message)
            failures.append(m)

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


def load_zipped_data_file_into_orm(
    model_to_model: list, unzipped_data_file_path: pathlib.Path
) -> bool:
    """
    This function takes a list of dictionary pairings, a Django model object and a layermapping object
    and a data source and uses all of them to load the data from the file into the
    corresponding Django model using the layermapping. The reason that you need a list is that some
    some data files have many layers and you want to load all of them.

    :param model_to_model: list
    :param unzipped_data_file_path: pathlib.Path
    :return: bool
    """

    successes = []
    failures = []
    model_definition = None  # Initialize to avoid UnboundLocalError

    try:
        message = "\n"
        message += f"About to start loading data from {unzipped_data_file_path} using {model_to_model}"
        logger.info(message)

        # first get the data file

        target_data_file = find_vector_dataset_file_in_directory(
            target_directory=unzipped_data_file_path
        )

        # GADM has a problem, see referred function docstring
        gadm_needle = "gadm_410-levels"
        logging.info(target_data_file.stem)
        if target_data_file.stem == gadm_needle:
            message = ""
            message += f"Working on GADM, {target_data_file}"
            logging.info(message)
            target_data_file = fix_gadm_null_foreign_keys(
                columns_to_fix=GADM_MODEL_FIELD_NAMES,
                source_gadm_dataset=target_data_file,
            )

        logger.info(target_data_file)

        # iterate through model to model list
        for mtm in model_to_model:

            # need the numerical index of the layer because it will be loaded correctly
            layer_index = model_to_model.index(mtm)

            # now assign the model name and mapping to variables
            # this can probably be done more efficiently but this works
            for mdl, mppng in mtm.items():
                model_definition = mdl
                layer_mapping = mppng

            message = "\n"
            message += f"Determined layer index, model and mapping: {layer_index}, {model_definition} {layer_mapping}"
            logger.info(message)

            # try clearing all the objects in memory if they exist

            model_definition.objects.all().delete()

            # now save the layermapping

            lm = LayerMapping(
                model_definition,
                target_data_file,
                layer_mapping,
                transform=True,
                layer=layer_index,
            )
            lm.save(verbose=False, strict=False)

            message = "\n"
            message += f"Successfully loaded data from {unzipped_data_file_path} for {model_definition}"
            logger.info(message)
            successes.append(model_definition)

    except Exception as e:
        message = "\n"
        message += f"There was an error loading data for model {model_definition} from {unzipped_data_file_path} : {e}"
        logger.error(message)
        failures.append(model_definition)

    # return test: count failures
    if len(failures) > 0:
        message = "\n FAILURE"
        message += f"\n The following models succeeded : {successes}"
        message += f"\n The following models failed : {failures}"

        logger.error(message)
        return False

    else:
        message = "\n SUCCESS"
        message += f"\n The following models succeeded : {successes}"
        message += f"\n The following models failed : {failures}"

        logger.info(message)
        return True


def fetch_and_unzip_the_file(model_to_work_on: str, url: str, data_type: str):
    # create path to file for download
    try:

        message = "\n"
        message += f"Working fetching the file for {model_to_work_on} from {url}"
        logger.info(message)

        data_path = DATA_TYPES_TO_PATH[data_type]

        local_filename = generate_local_path_from_url(
            url=url,
            directory_path=data_path,
        )

        message = f"Successfully generated {local_filename}"
        logger.debug(message)

        # checking if the file already exists so we don't lose time in downloading
        # this seems like an affectation but it will save a tremendous amount of time
        # over time

        # status variable
        valid_local_file_exists = False

        # get a hash from local filename

        message = "\n"
        message += f"Checking if local file exists for {local_filename}"
        logger.info(message)

        test_hash = generate_sha256_hash_for_file(local_filename)

        valid_local_file_exists = check_for_hash_in_dispatcher(
            target_file_path=local_filename,
            testing_hash_string=test_hash,
            confirmation_dict=FILE_NAMES_AND_HASHES,
        )

        if valid_local_file_exists:
            message = "\n"
            message += f"We already have a valid version of {local_filename}, no need to download"
            logger.info(message)

            unzipped_file_path = unzip_file_to_its_own_directory(
                path_to_zipfile=local_filename, new_dir_name=None, new_dir_parent=None
            )

            message = f"Successfully unzipped {unzipped_file_path}"
            logger.debug(message)

            return unzipped_file_path

        else:

            downloaded_file = download_file(
                url=url,
                local_filename=local_filename,
            )

            message = f"Successfully downloaded {downloaded_file}"
            logger.debug(message)

            unzipped_file_path = unzip_file_to_its_own_directory(
                path_to_zipfile=downloaded_file, new_dir_name=None, new_dir_parent=None
            )

            message = f"Successfully unzipped {unzipped_file_path}"
            logger.debug(message)

            return unzipped_file_path

    except Exception as e:
        message = f"There was an error: {e}"
        logger.error(message)


def fetch_and_load_all_data(model_to_work_on: str):
    message = f"Working on {model_to_work_on}"
    logger.info(message)

    try:
        # get params
        params = DOWNLOADS_DISPATCHER[model_to_work_on]

        url = params["url"]
        data_type = params["type"].upper()
        model_to_model = params["model_to_model"]

        logger.info(f"About to fetch and unzip the file from {url}")
        data_file = fetch_and_unzip_the_file(
            model_to_work_on=model_to_work_on, url=url, data_type=data_type
        )
        logger.info(f"Successfully fetched and unzipped data file from {url}")
        velvet_underground = load_zipped_data_file_into_orm(
            model_to_model=model_to_model, unzipped_data_file_path=data_file
        )

        logger.info(velvet_underground)

        message = "\n"
        message += (
            f"Successfully loaded all data for {model_to_work_on} from {data_file}"
        )
        logger.info(message)
        return True
    except Exception as e:
        message = "\n"
        message += (
            f"There was an error fetching and loading for {model_to_work_on}: {e}"
        )

        logger.error(message)
