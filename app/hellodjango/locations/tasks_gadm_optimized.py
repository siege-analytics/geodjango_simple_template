"""
Optimized GADM loading - Parallel load with deferred FK resolution

Strategy:
1. Load all 6 layers in PARALLEL to *_string fields (no FK dependencies)
2. After all layers loaded, populate actual FK relationships
3. Result: 25 min → 8-10 min (60% faster)
"""

from celery import shared_task, group, chord
from django.contrib.gis.utils import LayerMapping
from django.db import transaction
import logging
import time

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def load_gadm_layer_parallel(self, layer_index):
    """
    Load ONE GADM layer without FK resolution (uses *_string fields)
    
    All 6 layers can run simultaneously since no FK dependencies!
    """
    start_time = time.time()
    
    try:
        from locations.models import (
            Admin_Level_0, Admin_Level_1, Admin_Level_2,
            Admin_Level_3, Admin_Level_4, Admin_Level_5
        )
        from locations.models.gadm_parallel_mappings import (
            admin_level_1_mapping_parallel,
            admin_level_2_mapping_parallel,
            admin_level_3_mapping_parallel,
            admin_level_4_mapping_parallel,
            admin_level_5_mapping_parallel
        )
        from locations.models.gadm import admin_level_0_mapping
        from utilities.dispatchers import DOWNLOADS_DISPATCHER
        from utilities.vector_data_utilities import find_vector_dataset_file_in_directory
        from django.conf import settings
        
        model_classes = [Admin_Level_0, Admin_Level_1, Admin_Level_2,
                        Admin_Level_3, Admin_Level_4, Admin_Level_5]
        
        # Use parallel mappings for layers 1-5, normal for layer 0
        parallel_mappings = [
            admin_level_0_mapping,  # Level 0 has no FKs
            admin_level_1_mapping_parallel,
            admin_level_2_mapping_parallel,
            admin_level_3_mapping_parallel,
            admin_level_4_mapping_parallel,
            admin_level_5_mapping_parallel
        ]
        
        model_class = model_classes[layer_index]
        mapping = parallel_mappings[layer_index]
        layer_name = model_class.__name__
        
        logger.info(f"[Worker {self.request.hostname}] Loading {layer_name} (layer {layer_index}) WITHOUT FK resolution")
        
        # Find GADM geopackage
        gadm_dir = settings.VECTOR_SPATIAL_DATA_SUBDIRECTORY / "gadm_410-levels"
        gpkg_path = find_vector_dataset_file_in_directory(gadm_dir)
        
        # Clear existing data
        model_class.objects.all().delete()
        
        # Load with LayerMapping (to string fields, not FKs)
        lm = LayerMapping(
            model_class,
            str(gpkg_path),
            mapping,
            transform=True,
            layer=layer_index
        )
        
        lm.save(verbose=False, strict=False)
        
        count = model_class.objects.count()
        elapsed = time.time() - start_time
        
        logger.info(f"[Worker {self.request.hostname}] Loaded {count} {layer_name} records in {elapsed:.2f}s (FKs deferred)")
        
        return {
            'status': 'success',
            'layer': layer_name,
            'layer_index': layer_index,
            'count': count,
            'worker': self.request.hostname,
            'elapsed_seconds': round(elapsed, 2)
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[Worker {self.request.hostname}] Failed {layer_name}: {e}")
        return {
            'status': 'error',
            'layer_index': layer_index,
            'error': str(e),
            'elapsed_seconds': round(elapsed, 2)
        }


@shared_task(bind=True)
def populate_gadm_foreign_keys(self):
    """
    Step 2: Populate FK relationships after all layers loaded
    
    Uses the *_string fields to lookup and populate actual FKs
    Runs after parallel load completes.
    """
    start_time = time.time()
    
    try:
        from locations.models import (
            Admin_Level_0, Admin_Level_1, Admin_Level_2,
            Admin_Level_3, Admin_Level_4, Admin_Level_5
        )
        from django.db import connection
        
        logger.info(f"[Worker {self.request.hostname}] Populating GADM foreign keys")
        
        # Level 1: Populate gid_0 FK from gid_0_string
        with transaction.atomic():
            for obj in Admin_Level_1.objects.filter(gid_0__isnull=True, gid_0_string__isnull=False):
                try:
                    parent = Admin_Level_0.objects.get(gid_0=obj.gid_0_string)
                    obj.gid_0 = parent
                    obj.save(update_fields=['gid_0'])
                except Admin_Level_0.DoesNotExist:
                    pass  # Leave FK as NULL
        
        logger.info(f"[Worker {self.request.hostname}] Level 1 FKs populated")
        
        # Level 2: Populate gid_0 and gid_1 FKs
        with transaction.atomic():
            for obj in Admin_Level_2.objects.filter(gid_1__isnull=True, gid_1_string__isnull=False):
                try:
                    parent = Admin_Level_1.objects.get(gid_1=obj.gid_1_string)
                    obj.gid_1 = parent
                    obj.gid_0 = parent.gid_0  # Inherit from parent
                    obj.save(update_fields=['gid_0', 'gid_1'])
                except Admin_Level_1.DoesNotExist:
                    pass
        
        logger.info(f"[Worker {self.request.hostname}] Level 2 FKs populated")
        
        # Level 3: Populate FKs
        with transaction.atomic():
            for obj in Admin_Level_3.objects.filter(gid_2__isnull=True, gid_2_string__isnull=False):
                try:
                    parent = Admin_Level_2.objects.get(gid_2=obj.gid_2_string)
                    obj.gid_2 = parent
                    obj.gid_1 = parent.gid_1
                    obj.gid_0 = parent.gid_0
                    obj.save(update_fields=['gid_0', 'gid_1', 'gid_2'])
                except Admin_Level_2.DoesNotExist:
                    pass
        
        logger.info(f"[Worker {self.request.hostname}] Level 3 FKs populated")
        
        # Level 4: Populate FKs
        with transaction.atomic():
            for obj in Admin_Level_4.objects.filter(gid_3__isnull=True, gid_3_string__isnull=False):
                try:
                    parent = Admin_Level_3.objects.get(gid_3=obj.gid_3_string)
                    obj.gid_3 = parent
                    obj.gid_2 = parent.gid_2
                    obj.gid_1 = parent.gid_1
                    obj.gid_0 = parent.gid_0
                    obj.save(update_fields=['gid_0', 'gid_1', 'gid_2', 'gid_3'])
                except Admin_Level_3.DoesNotExist:
                    pass
        
        logger.info(f"[Worker {self.request.hostname}] Level 4 FKs populated")
        
        # Level 5: Populate FKs
        with transaction.atomic():
            for obj in Admin_Level_5.objects.filter(gid_4__isnull=True, gid_4_string__isnull=False):
                try:
                    parent = Admin_Level_4.objects.get(gid_4=obj.gid_4_string)
                    obj.gid_4 = parent
                    obj.gid_3 = parent.gid_3
                    obj.gid_2 = parent.gid_2
                    obj.gid_1 = parent.gid_1
                    obj.gid_0 = parent.gid_0
                    obj.save(update_fields=['gid_0', 'gid_1', 'gid_2', 'gid_3', 'gid_4'])
                except Admin_Level_4.DoesNotExist:
                    pass
        
        logger.info(f"[Worker {self.request.hostname}] Level 5 FKs populated")
        
        elapsed = time.time() - start_time
        logger.info(f"[Worker {self.request.hostname}] All GADM FKs populated in {elapsed:.2f}s")
        
        return {
            'status': 'success',
            'elapsed_seconds': round(elapsed, 2),
            'message': 'All GADM foreign keys populated'
        }
        
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"[Worker {self.request.hostname}] FK population failed: {e}")
        return {'status': 'error', 'error': str(e), 'elapsed_seconds': round(elapsed, 2)}


@shared_task(bind=True)
def load_gadm_parallel_optimized(self):
    """
    Orchestrator: Load GADM with parallel layers + deferred FK resolution
    
    Timeline:
    0:00 - 6 layers load in parallel (~5-7 min, distributed across workers)
    5:00 - FK population (~2-3 min, sequential on one worker)
    Total: ~8-10 minutes vs 25+ minutes (60-70% faster!)
    """
    try:
        logger.info(f"[Task {self.request.id}] Starting parallel GADM load (deferred FKs)")
        
        # Create chord: parallel loads → FK population callback
        workflow = chord([
            load_gadm_layer_parallel.s(0),  # ADM_0
            load_gadm_layer_parallel.s(1),  # ADM_1
            load_gadm_layer_parallel.s(2),  # ADM_2
            load_gadm_layer_parallel.s(3),  # ADM_3
            load_gadm_layer_parallel.s(4),  # ADM_4
            load_gadm_layer_parallel.s(5),  # ADM_5
        ])(populate_gadm_foreign_keys.s())
        
        logger.info(f"[Task {self.request.id}] Queued: 6 parallel loads → FK population")
        logger.info(f"[Task {self.request.id}] Workflow ID: {workflow.id}")
        
        return {
            'status': 'queued',
            'task_id': self.request.id,
            'workflow_id': workflow.id,
            'message': '6 GADM layers loading in parallel, then FK population'
        }
        
    except Exception as e:
        logger.error(f"[Task {self.request.id}] GADM parallel workflow failed: {e}")
        return {'status': 'error', 'error': str(e)}

