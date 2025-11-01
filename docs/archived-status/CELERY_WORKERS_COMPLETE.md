# Multiple Celery Workers - Complete ✅

**Date**: October 29, 2025  
**Status**: 3 Workers Running

## Configuration

### Workers Added
- `celery_worker_1` → `geodjango_celery_1`
- `celery_worker_2` → `geodjango_celery_2`
- `celery_worker_3` → `geodjango_celery_3`

Each worker:
- Uses same `geodjango_webserver` image
- Named worker: `worker1@hostname`, `worker2@hostname`, `worker3@hostname`
- Shares same Redis broker
- Independent task processing

### Scaling Strategy

**Horizontal Scaling**: Multiple containers, each running one Celery worker

```yaml
celery_worker_1:
  command: celery -A hellodjango worker -n worker1@%h
  
celery_worker_2:
  command: celery -A hellodjango worker -n worker2@%h
  
celery_worker_3:
  command: celery -A hellodjango worker -n worker3@%h
```

## Management Commands Refactored

### Added `--async` Flag

All data loading commands now support async execution:

```bash
# Synchronous (blocking, old way)
python manage.py fetch_and_load_standard_spatial_data gadm timezones

# Asynchronous (non-blocking, NEW)
python manage.py fetch_and_load_standard_spatial_data gadm timezones --async
```

### Commands with Async Support
1. `fetch_and_load_standard_spatial_data` → `fetch_and_load_standard_spatial_data_async`
2. `fetch_and_load_census_tiger_data` → `fetch_and_load_census_tiger_data_async`
3. `create_sample_places` → `create_sample_places_async`
4. `create_sample_addresses` → `create_sample_addresses_async`

### Task Wrapper Pattern

```python
class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("models", nargs="*")
        parser.add_argument('--async', action='store_true')
    
    def handle(self, *args, **kwargs):
        if kwargs.get('async'):
            # Queue as Celery task
            from locations.tasks import fetch_and_load_standard_spatial_data_async
            result = fetch_and_load_standard_spatial_data_async.delay(kwargs.get("models"))
            self.stdout.write(f'✅ Task queued: {result.id}')
            return
        
        # Run synchronously (original logic)
        # ... existing code ...
```

## Benefits

### Load Distribution
- 3 workers process tasks concurrently
- Heavy data loading doesn't block web server
- Tasks automatically distributed across workers

### Fault Tolerance
- If one worker dies, others continue
- Failed tasks can be retried
- Task state persisted in Redis

### Monitoring
```bash
# Check all workers
docker exec geodjango_celery_1 celery -A hellodjango inspect active

# View specific worker logs
docker logs geodjango_celery_1 -f
docker logs geodjango_celery_2 -f
docker logs geodjango_celery_3 -f
```

## Usage Examples

### Load Data Asynchronously
```bash
# Shell into webserver
make shell

# Queue spatial data loading
python hellodjango/manage.py fetch_and_load_standard_spatial_data --async

# Queue Census TIGER data
python hellodjango/manage.py fetch_and_load_census_tiger_data --async

# Queue sample places creation
python hellodjango/manage.py create_sample_places --async
```

### Direct Task Submission
```python
from locations.tasks import (
    fetch_and_load_standard_spatial_data_async,
    create_sample_places_async
)

# Submit task
result = fetch_and_load_standard_spatial_data_async.delay(['gadm', 'timezones'])

# Check status
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result (blocks until complete)
task_result = result.get(timeout=300)
```

## Architecture

```
┌────────────────────────────────────────┐
│         Django Management Command      │
│         (with --async flag)            │
└─────────────────┬──────────────────────┘
                  │
       ┌──────────┴──────────┐
       │                     │
   Sync Mode            Async Mode
   (blocking)        (non-blocking)
       │                     │
       ↓                     ↓
   Execute               Submit to
   Immediately             Redis
                             │
                    ┌────────┴────────┐
                    │                 │
                Worker Pool        Worker Pool
             (3 workers running)
                    │
                    ↓
            Task Execution
      (distributed across workers)
```

## Scaling Up/Down

### Add More Workers
Just duplicate a worker section in compose.yaml:

```yaml
celery_worker_4:
  <<: *celery_worker_1  # YAML anchor
  container_name: geodjango_celery_4
  command: celery -A hellodjango worker -n worker4@%h
```

### Reduce Workers
Comment out or remove worker sections from compose.yaml.

## Task Distribution

Tasks are distributed by Redis/Celery automatically using:
- Round-robin by default
- Can configure routing for specific tasks
- Can set task priorities

---

**Workers**: 3 running  
**Tasks**: Management commands + custom tasks  
**Distribution**: Automatic  
**Status**: Fully operational

