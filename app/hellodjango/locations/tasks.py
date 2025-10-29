"""
Celery tasks for locations app
"""

from celery import shared_task
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
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

