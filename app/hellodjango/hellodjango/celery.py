"""
Celery configuration for hellodjango project
"""

import os
from celery import Celery

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hellodjango.settings')

app = Celery('hellodjango')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related config keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Explicitly import task modules to ensure registration
# This happens after autodiscover_tasks() to ensure Django is ready
def _import_task_modules():
    try:
        from locations import tasks  # noqa: F401
        from locations import tasks_sedonadb  # noqa: F401
        from locations import tasks_gadm_optimized  # noqa: F401
        from locations import tasks_gadm_pipeline  # noqa: F401
        print("✅ All task modules imported successfully")
    except ImportError as e:
        print(f"⚠️ Error importing task modules: {e}")

# Call import after app is configured
_import_task_modules()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

