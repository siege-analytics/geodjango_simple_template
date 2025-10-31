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

# Explicitly register additional task modules beyond the standard tasks.py
# Celery autodiscover only finds tasks.py by default
app.autodiscover_tasks(['locations'], related_name='tasks_sedonadb', force=True)
app.autodiscover_tasks(['locations'], related_name='tasks_gadm_optimized', force=True)
app.autodiscover_tasks(['locations'], related_name='tasks_gadm_pipeline', force=True)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

