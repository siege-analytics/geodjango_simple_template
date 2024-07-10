# python imports

import os

#  django imports

from django.conf import settings

# log file

log_file_name = "django_application.log"
LOG_PATH = str(settings.LOGS_DIRECTORY / log_file_name)

if not os.path.exists(LOG_PATH):
    f = open(LOG_PATH, 'a').close()

# Create a LOGGING dictionary
LOGGING = {
    # Use v1 of the logging config schema
    'version': 1,
    # Continue to use existing loggers
    'disable_existing_loggers': False,
    # Add a verbose formatter
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
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
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
            'propagate': False,
        },
    },
}