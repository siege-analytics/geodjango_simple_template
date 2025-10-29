"""
Granular Celery tasks for breaking down slow management command operations
"""

from celery import shared_task, group, chain, chord
from django.core.management import call_command
from django.contrib.gis.geos import Point, fromstr
from .models import Place, United_States_Address
import logging
import time

logger = logging.getLogger(__name__)


# === Download and Load Tasks (Parallel Execution) ===

@shared_task(bind=True)
def download_spatial_dataset(self, model_name, url, destination_path):
    """
    Task: Download a single spatial dataset
    
    This is the slow I/O operation - downloading large files from internet
    """
    import requests
    from tqdm import tqdm
    import pathlib
    
    try:
        logger.info(f"[{self.request.id}] Downloading {model_name} from {url}")
        
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        dest_path = pathlib.Path(destination_path)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(dest_path, 'wb') as f:
            with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    pbar.update(len(chunk))
        
        logger.info(f"[{self.request.id}] Downloaded {model_name} ({total_size} bytes)")
        return {
            'status': 'success',
            'model': model_name,
            'size_bytes': total_size,
            'path': str(dest_path)
        }
    except Exception as e:
        logger.error(f"[{self.request.id}] Download failed for {model_name}: {e}")
        return {'status': 'error', 'model': model_name, 'error': str(e)}


@shared_task(bind=True)
def unzip_spatial_dataset(self, zip_file_path, extract_to_path):
    """
    Task: Unzip a downloaded spatial dataset
    
    This can be slow for large files
    """
    import zipfile
    import pathlib
    
    try:
        logger.info(f"[{self.request.id}] Unzipping {zip_file_path}")
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to_path)
        
        logger.info(f"[{self.request.id}] Unzipped to {extract_to_path}")
        return {
            'status': 'success',
            'path': str(extract_to_path)
        }
    except Exception as e:
        logger.error(f"[{self.request.id}] Unzip failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(bind=True)
def load_spatial_data_to_postgis(self, model_name, data_file_path, model_to_model_list):
    """
    Task: Load spatial data into PostGIS using Django LayerMapping
    
    This is CPU and I/O intensive - transforming geometries and bulk inserts
    """
    from django.contrib.gis.utils import LayerMapping
    import pathlib
    
    try:
        logger.info(f"[{self.request.id}] Loading {model_name} into PostGIS")
        
        data_file = pathlib.Path(data_file_path)
        
        for layer_index, mtm in enumerate(model_to_model_list):
            for model_class, field_mapping in mtm.items():
                logger.info(f"[{self.request.id}] Loading layer {layer_index}: {model_class.__name__}")
                
                # Clear existing data
                model_class.objects.all().delete()
                
                # Load data with LayerMapping
                lm = LayerMapping(
                    model_class,
                    str(data_file),
                    field_mapping,
                    transform=True,
                    layer=layer_index,
                )
                lm.save(verbose=False, strict=False)
                
                count = model_class.objects.count()
                logger.info(f"[{self.request.id}] Loaded {count} records for {model_class.__name__}")
        
        return {
            'status': 'success',
            'model': model_name,
            'worker': self.request.hostname
        }
    except Exception as e:
        logger.error(f"[{self.request.id}] PostGIS load failed for {model_name}: {e}")
        return {'status': 'error', 'model': model_name, 'error': str(e)}


# === Geocoding Tasks (Batch Processing) ===

@shared_task(bind=True)
def geocode_address_batch(self, address_batch):
    """
    Task: Geocode a batch of addresses using Nominatim
    
    This is slow - external API calls with rate limiting
    Batch size should be small (10-50) to avoid rate limits
    """
    from utilities.geocoding import geocode_address
    import time
    
    results = []
    
    for address_data in address_batch:
        try:
            # Rate limiting: sleep between requests
            time.sleep(1)  # Nominatim requires 1 second between requests
            
            result = geocode_address(
                street=address_data.get('street'),
                city=address_data.get('city'),
                state=address_data.get('state'),
                zip_code=address_data.get('zip')
            )
            
            results.append({
                'address_id': address_data.get('id'),
                'status': 'success',
                'lat': result.get('lat'),
                'lon': result.get('lon')
            })
            
        except Exception as e:
            logger.error(f"[{self.request.id}] Geocoding failed for address {address_data.get('id')}: {e}")
            results.append({
                'address_id': address_data.get('id'),
                'status': 'error',
                'error': str(e)
            })
    
    return {
        'status': 'success',
        'batch_size': len(address_batch),
        'results': results
    }


@shared_task(bind=True)
def bulk_create_places(self, places_data):
    """
    Task: Bulk create Place objects
    
    This is faster than individual saves
    """
    try:
        logger.info(f"[{self.request.id}] Bulk creating {len(places_data)} places")
        
        places = []
        for data in places_data:
            place = Place(
                name=data['name'],
                geom=fromstr(f"POINT({data['lon']} {data['lat']})", srid=4326)
            )
            places.append(place)
        
        Place.objects.bulk_create(places, batch_size=1000)
        
        logger.info(f"[{self.request.id}] Created {len(places)} places")
        return {
            'status': 'success',
            'created': len(places)
        }
    except Exception as e:
        logger.error(f"[{self.request.id}] Bulk create failed: {e}")
        return {'status': 'error', 'error': str(e)}


# === Parallel Model Loading (Using Celery Groups) ===

@shared_task(bind=True)
def load_single_spatial_model(self, model_name):
    """
    Task to load a single spatial model (GADM level, timezone, etc.)
    This allows parallel loading across multiple Celery workers.
    
    Args:
        model_name (str): Name of the model to load (e.g., 'gadm', 'timezones')
    
    Returns:
        dict: Status and timing info
    """
    start_time = time.time()
    
    try:
        logger.info(f"[Worker {self.request.hostname}] Loading model: {model_name}")
        
        from utilities.vector_data_utilities import fetch_and_load_all_data
        
        # This is the slow part - download, unzip, load to PostGIS
        result = fetch_and_load_all_data(model_name.lower())
        
        elapsed = time.time() - start_time
        logger.info(f"[Worker {self.request.hostname}] Loaded {model_name} in {elapsed:.2f}s")
        
        return {
            'status': 'success',
            'model': model_name,
            'worker': self.request.hostname,
            'elapsed_seconds': elapsed
        }
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[Worker {self.request.hostname}] Failed to load {model_name}: {e}")
        return {
            'status': 'error',
            'model': model_name,
            'worker': self.request.hostname,
            'elapsed_seconds': elapsed,
            'error': str(e)
        }


@shared_task(bind=True)
def parallel_load_all_spatial_data(self, models=None):
    """
    Orchestrator task: Loads multiple spatial models in parallel
    
    Uses Celery groups to distribute across workers
    Much faster than sequential loading
    """
    try:
        from utilities.dispatchers import DOWNLOADS_DISPATCHER
        
        # Determine which models to load
        if not models:
            models_to_load = list(DOWNLOADS_DISPATCHER.keys())
        else:
            models_to_load = [m for m in models if m.lower() in DOWNLOADS_DISPATCHER]
        
        logger.info(f"[Task {self.request.id}] Parallel loading {len(models_to_load)} models")
        
        # Create parallel task group
        job = group(
            load_single_spatial_model.s(model_name) 
            for model_name in models_to_load
        )
        
        # Execute in parallel
        result = job.apply_async()
        results = result.get(timeout=600)  # 10 minute timeout
        
        # Summarize results
        successful = [r for r in results if r['status'] == 'success']
        failed = [r for r in results if r['status'] == 'error']
        
        logger.info(f"[Task {self.request.id}] Complete: {len(successful)} succeeded, {len(failed)} failed")
        
        return {
            'status': 'success',
            'task_id': self.request.id,
            'models_loaded': len(successful),
            'models_failed': len(failed),
            'results': results
        }
    except Exception as e:
        logger.error(f"[Task {self.request.id}] Parallel load failed: {e}")
        return {
            'status': 'error',
            'task_id': self.request.id,
            'message': str(e)
        }


# === Chained Tasks (Download → Unzip → Load) ===

@shared_task
def download_unzip_load_chain(model_name, url, zip_path, extract_path, model_to_model):
    """
    Orchestrator: Chain tasks together for complete workflow
    
    download → unzip → load
    Each step runs separately, can retry individually
    """
    workflow = chain(
        download_spatial_dataset.s(model_name, url, zip_path),
        unzip_spatial_dataset.s(extract_path),
        load_spatial_data_to_postgis.s(model_name, extract_path, model_to_model)
    )
    
    result = workflow.apply_async()
    
    return {
        'status': 'queued',
        'model': model_name,
        'workflow_id': result.id
    }

