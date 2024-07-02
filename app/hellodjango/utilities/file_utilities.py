from django.conf import settings
import subprocess
import zipfile
import requests
from tqdm import tqdm

# logging.basicConfig(level=logging.INFO)

def run_subprocess(command_list):
    # Not sure if this is handling failures properly...
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    if p.returncode != 0:
        print("SUBPROCESS FAILED!")
        raise Exception("Subprocess failed with error: {}".format(stderr))

def download_file(url, local_filename):

    with requests.get(url, stream=True, allow_redirects=True) as r:

        if r.ok:
            logging.info(r.ok)
            total_size = int(r.headers.get('content-length',0))

            initial_pos = 0
            with open(local_filename, 'ab') as f:
                with tqdm(total=total_size, unit_scale=True, desc=local_filename, initial=initial_pos,
                          ascii=True) as pbar:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            pbar.update(len(chunk))
            return local_filename
        else:
            return False

def unzip_file_to_its_own_directory(path_to_zipfile, new_dir_name=None, new_dir_parent=None):
    try:
        frtz = zipfile.ZipFile(path_to_zipfile)
        if new_dir_name is None:
            new_dir_name = path_to_zipfile.stem
        if new_dir_parent is None:
            new_dir_parent = path_to_zipfile.parent

        # ensure that a directory exists for the new files to go in
        target_dir_for_unzipped_files = new_dir_parent / new_dir_name
        pathlib.Path(target_dir_for_unzipped_files).mkdir(parents=True, exist_ok=True)

        frtz.extractall(path=target_dir_for_unzipped_files)
        info_message = "Just unzipped: \n {path_to_zipfile} \n To: {target_dir}".format(
            **{'path_to_zipfile': path_to_zipfile,
               'target_dir': target_dir_for_unzipped_files})
        logging.info(info_message)
        return target_dir_for_unzipped_files

    except Exception as e:

        error_message = "There was an error {e}".format(**{'e': e})
        logging.error(error_message)
        return False

