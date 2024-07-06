# python stlib level imports

import os
import pathlib
import requests

# python library imports

from osgeo import gdal

# django imports

from django.conf import settings

# Logging

import logging

logger = logging.getLogger("django")


def find_vector_dataset_file_in_directory(
    target_directory: pathlib.Path,
) -> pathlib.Path:
    """
    This function takes a pathlib object and searches within it for the one file that:

    1. is a vector format spatial dataset

    #Parameters
    #       target_directory    :   string, the remote url for a file

    # Returns:
    #    Path object that shows the location of a vector format spatial dataset
    """
    try:
        message = "\n"
        message += f"Retrieving a vector spatial dataset in {target_directory}"
        logger.info(message)

        # first get all files in directory

        files_in_directory = [x for x in target_directory.glob("**/*") if x.is_file()]

        # now look to see which file matches both the directory name and having a valid suffix

        target_files_list = []

        for f in files_in_directory:

            lowered_file_stem = str(f.stem).lower()
            logger.info(lowered_file_stem)
            lowered_file_suffix = str(f.suffix).lower()
            logger.info(lowered_file_suffix)

            # logic test
            if lowered_file_suffix in settings.VALID_VECTOR_FILE_EXTENSIONS:
                target_files_list.append(f)
                logger.info(f"Added {f} to target_files_list")
            else:
                continue

        # success condition: found exactly one file
        if len(target_files_list) == 1:
            target_file = target_files_list[0]
            message = "\n"
            message += f"Found exactly one vector spatial dataset file in {target_directory}: {target_file}"
            logger.info(message)

            return target_file

        elif len(target_files_list) > 1:
            message = "\n"
            message += f"Found more than one vector spatial dataset file in {target_directory}: {files_in_directory}"
            logger.error(message)

            return False

        else:
            message = "\n"
            message += f"There are problems finding a vector spatial dataset in {target_directory}, here's the files list {files_in_directory}"
            logger.error(message)

            return False

    except Exception as e:
        message = "\n"
        message += f"There was an error retrieving a vector spatial dataset in {target_directory}: {e}"
        logger.error(message)
        return False
