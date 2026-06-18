# python imports

import logging
import os
from pathlib import Path

# read LOGS_DIRECTORY from the sibling path_settings module rather than
# from django.conf.settings. settings/__init__.py star-imports path_settings
# before this module loads, but django.conf.settings is a LazyObject that
# is not populated until Django finishes its first Settings(settings_module)
# boot. A cold star-import (test_settings doing `from .settings import *`)
# runs this module INSIDE Settings.__init__ and raises AttributeError on
# settings.LOGS_DIRECTORY. The sibling-module import resolves at compile
# time and does not depend on Django's settings machinery.

from .path_settings import LOGS_DIRECTORY

# log file

log_file_name = "django_application.log"
Path(LOGS_DIRECTORY).mkdir(parents=True, exist_ok=True)
LOG_PATH = str(Path(LOGS_DIRECTORY) / log_file_name)

# touch the log file so the FileHandler does not fail on first write
try:
    Path(LOG_PATH).touch(exist_ok=True)
except Exception as e:
    message = "\n"
    message += f"Pathlib method to create the logging file didn't work, trying OS lib method:{e}"
    logging.error(message)
try:
    if not os.path.exists(LOG_PATH):
        f = open(LOG_PATH, 'w+').close()
except Exception as e:
    message = "\n"
    message += f"OS method to create the logging file didn't work, Alfred E. Neumann:{e}"
    logging.error(message)


# Create a LOGGING dictionary
LOGGING = {
    # Use v1 of the logging config schema
    'version': 1,
    # Continue to use existing loggers
    'disable_existing_loggers': False,
    # Add a verbose formatter
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {funcName} {filename:s} {lineno:d} {message}',
            'style': '{',
        },
    },
    # Create a log handler that prints logs to the terminal
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            # Add the verbose formatter
            'formatter': 'verbose',
        },
        # Add a handler to write logs to a file
        'file': {
            # Use the FileHandler class
            'class': 'logging.FileHandler',
            # Specify a local log file as a raw string. Use your app's directory.
            'filename': LOG_PATH,
            'formatter': 'verbose',
        },
    },
    # Define the root logger's settings
    'root': {
        # Use the console and file logger
        'handlers': ['console', 'file'],
        'level': 'DEBUG',
    },
    # Define the django log module's settings
    'loggers': {
        'django': {
            # Use the console and file logger
            'handlers': ['console', 'file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
