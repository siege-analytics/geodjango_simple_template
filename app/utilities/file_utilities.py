import hashlib

from django.conf import settings
import pathlib
import requests
import subprocess
from tqdm import tqdm

import zipfile

# Logging

import logging

logger = logging.getLogger("django")


def run_subprocess(command_list):
    # Not sure if this is handling failures properly...
    p = subprocess.Popen(
        command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        logger.error("SUBPROCESS FAILED!")
        raise Exception("Subprocess failed with error: {}".format(stderr))


def ensure_path_exists(desired_path: pathlib.Path) -> pathlib.Path:

    try:
        desired_path_object = pathlib.Path(desired_path)
        pathlib.Path(desired_path_object).mkdir(parents=True, exist_ok=True)
        return desired_path_object

    except Exception as e:
        message = f"Exception while generating local path: {e}"
        logger.error(message)
        return False


def generate_local_path_from_url(
    url: str, directory_path: pathlib.Path, as_string: bool = True
):

    # Returns a pathlib path to a file

    # Parameters:
    #       url             :   string, the remote url for a file
    #       directory_name  :   path, the directory to white the file should be saved
    #       as_string       :   bool, toggles whether object is returned as string or path

    # Returns:
    #    Path object that concatenates the file name to a directory path

    try:
        remote_file_name = url.split("/")[-1]
        directory_path = pathlib.Path(directory_path)

        new_path = directory_path / remote_file_name

        if as_string is True:
            new_path = str(new_path)
        message = f"Successfully generated path {new_path}, as_string={as_string}"
        logger.debug(message)
        return new_path

    except Exception as e:
        message = f"Exception while generating local path: {e}"
        logger.error(message)
        return False


def download_file(url, local_filename):

    with requests.get(url, stream=True, allow_redirects=True) as r:

        if r.ok:
            logging.info(r.ok)
            total_size = int(r.headers.get("content-length", 0))

            initial_pos = 0
            with open(local_filename, "wb") as f:
                with tqdm(
                    total=total_size,
                    unit_scale=True,
                    desc=local_filename,
                    initial=initial_pos,
                    ascii=True,
                ) as pbar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            pbar.update(len(chunk))
            return local_filename
        else:
            return False


def unzip_file_to_its_own_directory(
    path_to_zipfile: pathlib.Path, new_dir_name=None, new_dir_parent=None
):
    try:
        path_to_zipfile = pathlib.Path(path_to_zipfile)
        frtz = zipfile.ZipFile(path_to_zipfile)
        if new_dir_name is None:
            new_dir_name = path_to_zipfile.stem
        if new_dir_parent is None:
            new_dir_parent = path_to_zipfile.parent

        # ensure that a directory exists for the new files to go in
        target_dir_for_unzipped_files = new_dir_parent / new_dir_name

        pathlib.Path(target_dir_for_unzipped_files).mkdir(parents=True, exist_ok=True)

        frtz.extractall(path=target_dir_for_unzipped_files)
        message = f"Just unzipped: \n {path_to_zipfile} \n To: {target_dir_for_unzipped_files}"
        logger.info(message)
        return target_dir_for_unzipped_files

    except Exception as e:

        message = f"There was an error: {e}"
        logger.error(message)
        return False


def generate_sha256_hash_for_file(target_file: pathlib.Path) -> str:

    # Returns string representation of a sha256 hash of a file
    # based on # https://gist.github.com/jakekara/078899caaf8d5e6c74ef58d16ce7e703

    # Parameters:
    #       target_file     :   the file for which we want a hash

    # Returns:
    #    string that contains the sha256 hash of the file

    # container variables
    h256 = hashlib.sha256()
    try:
        target_file = pathlib.Path(target_file)
        file_check = target_file.is_file()
        if file_check:

            h256.update(open(target_file, "rb").read())
            text_of_hash = h256.hexdigest()
            message = "\n"
            message += f"SUCCESS: Generated hash for {target_file}\n: {text_of_hash}"
            logger.debug(message)
            return text_of_hash
        else:
            message = "\n"
            message += f"ERROR: Could not generate hash for {target_file} because it is not a file"
            logger.error(message)
            return False
    except Exception as e:
        message = "\n"
        message += f"ERROR: Could not generate hash for {target_file}: {e}"
        logger.error(message)
        return False


def add_hash_entry_to_dispatcher(
    target_file: pathlib.Path, confirmation_dict: dict
) -> bool:
    """

    :param target_file: pathlib.Path object that we are going to add to the dispatcher
    :param confirmation_dict: dict object that contains file names and valid hashes
    :return: bool
    """

    try:
        # ensure that we have a pathlib.Path object so that we can get a name
        target_file_path = pathlib.Path(target_file)
        file_name_and_extension = str(target_file_path.name)

        # get hash for path

        new_hash_for_file = generate_sha256_hash_for_file(target_file_path)

        # file_name_and_extension_is needle, confirmation_dict is haystack

        needle = file_name_and_extension
        haystack = confirmation_dict

        # logic checks

        # 1. Do we have an entry?
        # 2. Does the entry match?

        if needle in haystack:
            found_hash = haystack[needle]
            message = "\n"
            message += f"Found an entry for {file_name_and_extension} in {confirmation_dict}: {found_hash}"
            haystack[needle] = new_hash_for_file
            message += "\n"
            message += f"SUCCESS: Replaced old hash for {file_name_and_extension} in {confirmation_dict} with: {new_hash_for_file}"
            logger.info(message)
            return True

        elif needle not in haystack:
            message = "\n"
            message += f"No entry found for {file_name_and_extension} in {confirmation_dict}, adding {new_hash_for_file} "
            haystack[needle] = new_hash_for_file
            message += "\n"
            message += f"SUCCESS: Replaced old hash for {file_name_and_extension} in {confirmation_dict} with: {new_hash_for_file}"
            logger.info(message)
            return True

        else:
            message = "\n"
            message += f"FAILURE: Was not able to add an entry for {file_name_and_extension} to {confirmation_dict}, please add one"
            logger.error(message)

    except Exception as e:
        message = "\n"
        message += f"FAILURE: Exception while searching for hash for {target_file_path} in {confirmation_dict}: {e}"
        logger.error(message)
        return False


def check_for_hash_in_dispatcher(
    target_file_path: pathlib.Path, testing_hash_string: str, confirmation_dict: dict
) -> bool:

    try:
        # ensure that we have a pathlib.Path object so that we can get a name
        target_file_path = pathlib.Path(target_file_path)
        file_name_and_extension = str(target_file_path.name)

        # file_name_and_extension_is needle, confirmation_dict is haystack

        needle = file_name_and_extension
        haystack = confirmation_dict.keys()

        # logic checks

        # 1. Do we have an entry?
        # 2. Does the entry match?

        if needle in haystack:
            message = "\n"
            message += (
                f"Found an entry for {file_name_and_extension} in {confirmation_dict}"
            )
            logger.info(message)

            known_good_hash = confirmation_dict[needle]

            if testing_hash_string == known_good_hash:
                message = "\n"
                message += f"SUCCESS: Found hash for {target_file_path} in {confirmation_dict} that matches"
                logger.info(message)
                return True

        else:
            message = "\n"
            message += f"FAILURE: Did not find an entry for {file_name_and_extension} in {confirmation_dict}, please add one"
            logger.error(message)
            return False

    except Exception as e:
        message = "\n"
        message += f"FAILURE: Exception while searching for hash for {target_file_path} in {confirmation_dict}: {e}"
        logger.error(message)
        return False
