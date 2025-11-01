# python stlib level imports

import os
import pathlib
import requests

# python library imports

from osgeo import gdal
import geopandas as gpd
import numpy as np

# django imports

from django.conf import settings

# Logging

import logging

logger = logging.getLogger("django")

# CONSTANTS

GADM_MODEL_FIELD_NAMES = [
    "GID_0",
    "GID_1",
    "GID_2",
    "GID_3",
    "GID_4",
    "GID_5",
]


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

        target_directory = pathlib.Path(target_directory)

        permitted_gdb_substring = "gdb"

        files_in_directory = [
            x
            for x in target_directory.glob("**/*")
            if x.is_file() or permitted_gdb_substring in pathlib.Path(x.name)
        ]

        # now look to see which file matches both the directory name and having a valid suffix

        target_files_list = []

        for f in files_in_directory:

            lowered_file_suffix = str(f.suffix).lower()

            # logic test
            if lowered_file_suffix in settings.VALID_VECTOR_FILE_EXTENSIONS:
                target_files_list.append(f)
                logger.debug(f"Added {f} to target_files_list")
            else:
                continue

        number_of_files_in_target_files_list = len(target_files_list)
        # success condition: found exactly one file
        if number_of_files_in_target_files_list == 1:
            target_file = target_files_list[0]
            message = "\n"
            message += f"SUCCESS: Found exactly one vector spatial dataset file in {target_directory}: {target_file}"
            logger.info(message)

            return target_file

        elif number_of_files_in_target_files_list > 1:
            message = "\n"
            message += f"Found more than one vector spatial dataset file in {target_directory}: {files_in_directory}"
            logger.error(message)

            return False

        else:
            message = "\n"
            message += f"There were problems finding a vector spatial dataset in {target_directory}, here's the files list {files_in_directory}"
            logger.error(message)

            return False

    except Exception as e:
        message = "\n"
        message += f"There was an error retrieving a vector spatial dataset in {target_directory}: {e}"
        logger.error(message)
        return False


def fix_gadm_null_foreign_keys(
    source_gadm_dataset: pathlib.Path, columns_to_fix=GADM_MODEL_FIELD_NAMES
) -> pathlib.Path:
    """
    The GADM dataset has a string value of `NA` as String where it should be None for several fields.
    This function:
    1. Checks hash-based cache to see if cleaning already done
    2. If cache hit, returns cached cleaned file (skips work)
    3. Otherwise: iterates over every layer, replaces NA with np.nan, saves to new GPKG
    4. Updates cache with hash of cleaned file
    5. Returns the cleaned GPKG

    :param source_gadm_dataset:
    :return: pathlib.Path to cleaned dataset
    """
    from utilities.dataset_cache import (
        check_if_cleaning_needed,
        update_cache_after_cleaning
    )
    
    # Check cache first - skip cleaning if file unchanged
    data_dir = source_gadm_dataset.parent
    needs_cleaning, cached_path = check_if_cleaning_needed(source_gadm_dataset, data_dir)
    
    if not needs_cleaning and cached_path:
        logger.info(f"✅ Using cached cleaned file (hash match): {cached_path}")
        return cached_path
    
    message = ""
    message += "The GADM dataset has a string value of `NA` as None for several fields."
    message += "We have to fix this using a function."
    logging.info(message)

    try:
        # configure outfile from source
        new_gpkg_stem = f"{source_gadm_dataset.stem}_fixed"

        new_gpkg_path = settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY / new_gpkg_stem

        new_gpkg_path.mkdir(parents=True, exist_ok=True)
        new_gpkg_name = f"{new_gpkg_stem}{source_gadm_dataset.suffix}"

        target_gpkg = new_gpkg_path / new_gpkg_name
        message = ""
        message += f"New file and path: {target_gpkg}"
        logging.info(target_gpkg)

        # configure layers from source
        gadm_layers = gpd.list_layers(source_gadm_dataset)["name"].tolist()
        # message = ""
        # message += f"GADM layers: {gadm_layers}"
        # logging.info(message)

        for g in gadm_layers:
            logging.info(f"Working on layer: {g}")

            gdf = gpd.read_file(source_gadm_dataset, layer=g)
            logging.info(f"Layer {g} has columns: {list(gdf)}")

            # Fix ALL columns first, THEN write once (not per column!)
            columns_fixed = []
            for c in columns_to_fix:
                if c in list(gdf):
                    message = f"Layer {g} fixing column: {c}"
                    logging.info(message)
                    gdf[c] = gdf[c].replace("NA", np.nan)
                    columns_fixed.append(c)
            
            # Write ONCE after all columns fixed
            if columns_fixed:
                result = gdf.to_file(target_gpkg, driver="GPKG", layer=g)
                message = f"Layer {g} written with {len(columns_fixed)} columns fixed: {columns_fixed}"
                logging.info(message)

        # Update cache with hash of cleaned file
        update_cache_after_cleaning(source_gadm_dataset, target_gpkg, data_dir)
        logger.info(f"✅ Cleaning complete - cached for future runs")

        return target_gpkg

    except Exception as e:
        message = f"Exception trying to replace nulls in layer: {e}"
        logging.error(message)
        return source_gadm_dataset
