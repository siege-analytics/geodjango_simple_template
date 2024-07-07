# Imports
import pathlib

# Django Management Command Imports

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

# Generic Python Library Imports

import sys, os
import importlib.util

# custom functions and data

# from utilities.file_utilities import *
from utilities import *


class Command(BaseCommand):
    args = ""
    help = "Fetches data specified by CLI argument, data must be in the dispatcher"

    def add_arguments(self, parser):
        parser.add_argument("models", nargs="*")

    def handle(self, *args, **kwargs):

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

        print(models_that_cannot_be_worked_on)
        print(models_to_work_on)

        # start work
        try:
            for m in models_to_work_on:
                m = m.lower()
                fetch_and_load_all_data(m)
                successes.append(m)
        except Exception as e:
            message = (
                "There was an error at the management command level working on {m}: {e}"
            )
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

    try:
        message = "\n"
        message += f"About to start loading data from {unzipped_data_file_path} using {model_to_model}"
        logger.info(message)

        # first get the data file

        target_data_file = find_vector_dataset_file_in_directory(
            target_directory=unzipped_data_file_path
        )

        print(target_data_file)

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
            lm.save(verbose=False, strict=True)

            message = "\n"
            message += f"Successfully loaded data from {unzipped_data_file_path} for {model_definition}"
            logger.info(message)

    except Exception as e:
        message = "\n"
        message += f"There was an error loading data for model {model_definition} from {unzipped_data_file_path} : {e}"
        logger.error(message)
        return False


def fetch_and_unzip_the_file(model_to_work_on: str, url: str, data_type: str):
    # create path to file for download
    try:
        data_path = DATA_TYPES_TO_PATH[data_type]

        local_filename = generate_local_path_from_url(
            url=url,
            directory_path=data_path,
        )
        message = f"Successfully generated {local_filename}"
        logger.debug(message)

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
        print(message)


def fetch_and_load_all_data(model_to_work_on: str):
    message = f"Working on {model_to_work_on}"
    print(message)

    try:
        # get params
        params = DOWNLOADS_DISPATCHER[model_to_work_on]

        url = params["url"]
        data_type = params["type"].upper()
        model_to_model = params["model_to_model"]

        data_file = fetch_and_unzip_the_file(
            model_to_work_on=model_to_work_on, url=url, data_type=data_type
        )

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
