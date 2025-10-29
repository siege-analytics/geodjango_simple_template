"""
Celery tasks for locations app
"""

from celery import shared_task
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.core.management import call_command
from .models import Place
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_location_update(location_id):
    """
    Example task: Process a location update
    """
    try:
        place = Place.objects.get(id=location_id)
        logger.info(f"Processing location update for {place.name}")
        # Do something with the location
        return {
            'status': 'success',
            'location_id': location_id,
            'name': place.name
        }
    except Place.DoesNotExist:
        logger.error(f"Place {location_id} not found")
        return {'status': 'error', 'message': 'Place not found'}


@shared_task
def geocode_addresses_batch(address_ids):
    """
    Example task: Batch geocode addresses
    """
    logger.info(f"Batch geocoding {len(address_ids)} addresses")
    # Implement your geocoding logic here
    return {
        'status': 'success',
        'processed': len(address_ids)
    }


@shared_task
def calculate_distances(from_location_id, to_location_ids):
    """
    Example task: Calculate distances between locations
    """
    try:
        from_place = Place.objects.get(id=from_location_id)
        results = []
        
        for to_id in to_location_ids:
            try:
                to_place = Place.objects.get(id=to_id)
                # Calculate distance
                distance = from_place.geom.distance(to_place.geom) if from_place.geom and to_place.geom else None
                results.append({
                    'from': from_place.name,
                    'to': to_place.name,
                    'distance_degrees': distance
                })
            except Place.DoesNotExist:
                continue
        
        return {
            'status': 'success',
            'calculations': results
        }
    except Place.DoesNotExist:
        return {'status': 'error', 'message': 'Origin place not found'}


@shared_task
def cleanup_old_locations():
    """
    Example periodic task: Clean up old or invalid locations
    """
    logger.info("Running location cleanup task")
    # Implement cleanup logic
    return {'status': 'success', 'message': 'Cleanup complete'}


# === Management Command Tasks ===
# These wrap existing management commands for async execution

@shared_task(bind=True)
def fetch_and_load_standard_spatial_data_async(self, models=None):
    """
    Async task: Fetch and load standard spatial data (GADM, timezones, etc.)
    
    Args:
        models (list): Optional list of models to load. If None, loads all.
    
    Returns:
        dict: Status and results
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting spatial data fetch")
        
        # Call the management command
        if models:
            call_command('fetch_and_load_standard_spatial_data', *models)
        else:
            call_command('fetch_and_load_standard_spatial_data')
        
        logger.info(f"[Task {self.request.id}] Spatial data fetch complete")
        return {
            'status': 'success',
            'task_id': self.request.id,
            'message': 'Spatial data loaded successfully'
        }
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Failed to load spatial data: {e}")
        return {
            'status': 'error',
            'task_id': self.request.id,
            'message': str(e)
        }


@shared_task(bind=True)
def fetch_and_load_census_tiger_data_async(self, models=None):
    """
    Async task: Fetch and load US Census TIGER data
    
    Args:
        models (list): Optional list of models to load
    
    Returns:
        dict: Status and results
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting Census TIGER data fetch")
        
        if models:
            call_command('fetch_and_load_census_tiger_data', *models)
        else:
            call_command('fetch_and_load_census_tiger_data')
        
        logger.info(f"[Task {self.request.id}] Census TIGER data fetch complete")
        return {
            'status': 'success',
            'task_id': self.request.id,
            'message': 'Census TIGER data loaded successfully'
        }
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Failed to load Census TIGER data: {e}")
        return {
            'status': 'error',
            'task_id': self.request.id,
            'message': str(e)
        }


@shared_task(bind=True)
def create_sample_places_async(self):
    """
    Async task: Create sample places from pharmacy data
    
    Returns:
        dict: Status and results
    """
    try:
        logger.info(f"[Task {self.request.id}] Creating sample places")
        
        call_command('create_sample_places')
        
        logger.info(f"[Task {self.request.id}] Sample places created")
        return {
            'status': 'success',
            'task_id': self.request.id,
            'message': 'Sample places created successfully'
        }
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Failed to create sample places: {e}")
        return {
            'status': 'error',
            'task_id': self.request.id,
            'message': str(e)
        }


@shared_task(bind=True)
def create_sample_addresses_async(self):
    """
    Async task: Create sample addresses
    
    Returns:
        dict: Status and results
    """
    try:
        logger.info(f"[Task {self.request.id}] Creating sample addresses")
        
        call_command('create_sample_addresses')
        
        logger.info(f"[Task {self.request.id}] Sample addresses created")
        return {
            'status': 'success',
            'task_id': self.request.id,
            'message': 'Sample addresses created successfully'
        }
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Failed to create sample addresses: {e}")
        return {
            'status': 'error',
            'task_id': self.request.id,
            'message': str(e)
        }

