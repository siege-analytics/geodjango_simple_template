# Mac Mini Deployment Guide - GeoDjango Simple Template

**Target**: Mac Mini M2 (or later) with 16GB+ RAM  
**Purpose**: Production geospatial API server with GADM data

---

## Pre-Deployment Checklist

### Mac Mini Setup
- [ ] macOS Sonoma or later installed
- [ ] Docker Desktop installed and running
- [ ] Git configured with SSH keys for GitHub
- [ ] Homebrew installed
- [ ] Network configured (static IP recommended)

### Docker Configuration
```bash
# Open Docker Desktop > Settings > Resources
# Configure:
Memory: 12GB (minimum 8GB)
CPUs: 4-6 (use all available)
Swap: 2GB
Disk image size: 100GB+

# Verify after setting:
docker info | grep -E "Memory|CPUs"
```

### Network Access
- [ ] Port 8000 accessible (Django API)
- [ ] Port 8001 accessible (Nginx)  
- [ ] Port 5555 accessible (Flower monitoring)
- [ ] Port 54322 accessible (PostGIS - if remote access needed)

---

## Deployment Steps

### Step 1: Clone Repository

```bash
cd ~/Code  # or preferred location
git clone git@github.com:siege-analytics/geodjango_simple_template.git
cd geodjango_simple_template
```

### Step 2: Build Docker Images

```bash
# This will take 10-15 minutes on first build
make build

# Expected output:
# - geodjango_webserver (with Celery, Flower, SedonaDB)
# - geodjango_nginx
# - Plus postgis and redis from Docker Hub
```

### Step 3: Start Services

```bash
make up

# Verify all 8 services running:
docker ps

# Expected containers:
# - geodjango_webserver (Daphne ASGI server)
# - geodjango_nginx (reverse proxy)
# - geodjango_postgis (PostGIS database)
# - geodjango_redis (Celery broker)
# - geodjango_celery_1, _2, _3 (workers)
# - geodjango_flower (monitoring UI)
```

### Step 4: Verify Services

```bash
# Check Celery workers are registered
docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect registered

# Should see locations.tasks.* including:
# - load_gadm_pipelined
# - preprocess_single_gadm_layer
# - load_preprocessed_gadm_layer
# - populate_gadm_foreign_keys_fast

# Test Flower UI
open http://localhost:5555
# Should see 3 workers online

# Test Django API
curl http://localhost:8000/locations/places/
# Should return JSON (even if empty initially)
```

### Step 5: Run Database Migrations

```bash
make shell  # Opens shell in webserver container

# Inside container:
python hellodjango/manage.py migrate

# Verify admin level tables exist
python hellodjango/manage.py dbshell
\dt locations_admin_level*
\d locations_admin_level_1
# Verify gid_*_string columns exist
\q

exit  # Exit container shell
```

### Step 6: Load GADM Data

```bash
# Submit async task (from Mac Mini terminal, NOT in container)
docker exec geodjango_webserver sh -c "cd /usr/src/app/hellodjango && python -c '
import os, django, time
os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"hellodjango.settings\")
django.setup()
from locations.tasks import load_gadm_pipelined

print(\"🚀 Starting GADM load at:\", time.strftime(\"%H:%M:%S\"))
result = load_gadm_pipelined.delay()
print(f\"Task ID: {result.id}\")
print(f\"Monitor: http://localhost:5555/task/{result.id}\")
print(\"Expected duration: 8-10 minutes\")
'"

# Monitor progress (choose one):

# Option 1: Flower UI (recommended)
open http://localhost:5555

# Option 2: Worker logs
docker logs -f geodjango_celery_1

# Option 3: All workers
docker logs -f geodjango_celery_1 geodjango_celery_2 geodjango_celery_3 | grep -E "Preprocessing|Preprocessed|Loading|Loaded|FK population"
```

###  Step 7: Verify Data Load

```bash
# Check record counts
docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c "
SELECT 'Admin_Level_0' as level, COUNT(*) as records FROM locations_admin_level_0
UNION ALL
SELECT 'Admin_Level_1', COUNT(*) FROM locations_admin_level_1
UNION ALL  
SELECT 'Admin_Level_2', COUNT(*) FROM locations_admin_level_2
UNION ALL
SELECT 'Admin_Level_3', COUNT(*) FROM locations_admin_level_3
UNION ALL
SELECT 'Admin_Level_4', COUNT(*) FROM locations_admin_level_4
UNION ALL
SELECT 'Admin_Level_5', COUNT(*) FROM locations_admin_level_5;
"

# Expected totals:
# Admin_Level_0: 263 (countries)
# Admin_Level_1: ~50,000 (states/provinces)
# Admin_Level_2: ~144,000 (counties)
# Admin_Level_3: ~144,000
# Admin_Level_4: ~80,000
# Admin_Level_5: ~51,000

# Check ForeignKey relationships
docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c "
SELECT 
    l1.name_1, 
    l0.country as parent_country
FROM locations_admin_level_1 l1
JOIN locations_admin_level_0 l0 ON l1.gid_0_id = l0.id
LIMIT 10;
"

# Should show state/province names with their parent countries
```

### Step 8: Test API Endpoints

```bash
# Get all countries
curl http://localhost:8000/locations/admin_level_0s/ | jq '.' | head -50

# Get US states
curl "http://localhost:8000/locations/admin_level_1s/?gid_0__country=United%20States" | jq '.results[].name_1'

# Get places (if sample data loaded)
curl http://localhost:8000/locations/places/ | jq '.'
```

---

## Monitoring & Maintenance

### Check Service Health
```bash
# All containers
docker ps

# Check logs
docker logs geodjango_webserver  # Django logs
docker logs geodjango_celery_1   # Worker 1 logs
docker logs geodjango_nginx       # Nginx logs

# Check PostGIS
docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c "SELECT postgis_version();"
```

### Restart Services
```bash
# Restart specific service
docker restart geodjango_webserver

# Restart all
make restart

# Or
make down
make up
```

### Update Code
```bash
cd ~/Code/geodjango_simple_template
git pull origin main
make down
make build  # Rebuild if requirements changed
make up
```

---

## Troubleshooting

### Workers Not Starting
```bash
# Check logs
docker logs geodjango_celery_1

# Common issues:
# 1. "Module 'hellodjango' has no attribute 'celery'"
#    → Check hellodjango/__init__.py exports celery module
#
# 2. "No module named 'locations'"
#    → Check working directory in compose.yaml (should be /usr/src/app/hellodjango)
#
# 3. Workers restart loop
#    → Check memory allocation, may need to reduce workers
```

### Out of Memory
```bash
# Check Docker memory
docker info | grep Memory

# If OOM persists:
# 1. Increase Docker memory allocation
# 2. Or reduce workers in compose.yaml:
#    Comment out celery_3 service
# 3. Or run sequentially instead of parallel (slower but stable)
```

### GADM Load Fails
```bash
# Check if file exists
docker exec geodjango_webserver ls -lh /usr/src/app/data/spatial/vector/gadm_410-levels/

# If missing:
make shell
python hellodjango/manage.py fetch_and_load_standard_spatial_data gadm
# This downloads the file first

# Check preprocessing cache
docker exec geodjango_webserver ls -lh /usr/src/app/data/spatial/vector/gadm_410-levels/gadm_410-levels_fixed/
```

### FK Resolution Fails
```bash
# Check if gid_*_string fields have data
docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c "
SELECT gid_0_string, gid_1_string, name_1
FROM locations_admin_level_1
LIMIT 5;
"

# If empty, layers didn't load to string fields
# Rerun with: load_gadm_pipelined.delay()
```

---

## Performance Monitoring

### Real-Time Monitoring
```bash
# Watch worker activity
watch -n 5 'docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect active'

# Watch resource usage
watch -n 2 'docker stats --no-stream'

# Flower UI (best option)
open http://localhost:5555
# Shows: task states, worker health, task history
```

### Post-Load Analysis
```bash
# Check task duration in Flower
# Or query Celery result backend
docker exec geodjango_webserver sh -c "cd /usr/src/app/hellodjango && python manage.py shell" <<'PYTHON'
from django_celery_results.models import TaskResult
import json

# Get recent GADM tasks
gadm_tasks = TaskResult.objects.filter(
    task_name__contains='gadm'
).order_by('-date_done')[:10]

for task in gadm_tasks:
    result = json.loads(task.result) if task.result else {}
    print(f"{task.task_name}: {task.status}")
    print(f"  Duration: {result.get('elapsed_seconds', 'N/A')}s")
    print(f"  Worker: {result.get('worker', 'N/A')}")
    print()
PYTHON
```

---

## File Transfer to Mac Mini

### Option 1: Git (Recommended)
```bash
# On Mac Mini:
git clone git@github.com:siege-analytics/geodjango_simple_template.git
# Everything is in the repo
```

### Option 2: If Data Files Needed
```bash
# From Mac Laptop:
# Find data directory
ls -lh geodjango_simple_template/app/data/spatial/vector/

# Copy via rsync if data already downloaded (saves download time)
rsync -avz --progress \
  geodjango_simple_template/app/data/spatial/vector/gadm_410-levels/ \
  macmini:~/Code/geodjango_simple_template/app/data/spatial/vector/gadm_410-levels/

# Or use AirDrop for smaller files
```

### Option 3: Fresh Start (Recommended)
```bash
# On Mac Mini: let it download fresh
# This ensures clean state and tests download logic
make shell
python hellodjango/manage.py fetch_and_load_standard_spatial_data gadm
```

---

## Production Considerations

### Security
- [ ] Change default passwords in `compose.yaml`
- [ ] Set `DEBUG=0` in production
- [ ] Configure allowed hosts properly
- [ ] Set up SSL/TLS if exposing publicly

### Backups
```bash
# Backup PostGIS database
docker exec geodjango_postgis pg_dump -U dheerajchand geodjango_database > backup_$(date +%Y%m%d).sql

# Restore
docker exec -i geodjango_postgis psql -U dheerajchand geodjango_database < backup_20251107.sql
```

### Monitoring
- Set up Flower authentication
- Configure log rotation
- Monitor disk space (datasets can be large)

---

## Expected Timeline (Mac Mini)

1. **Setup** (30 min)
   - Clone repo: 2 min
   - Build images: 15 min
   - Start services: 2 min
   - Run migrations: 1 min
   - Verify setup: 10 min

2. **GADM Load** (10-15 min)
   - Download: 2-3 min (if not cached)
   - Preprocessing (6 layers parallel): 3-4 min
   - PostGIS loading (parallel): 4-5 min
   - FK resolution: 2-3 min

3. **Verification** (5 min)
   - Record counts: 1 min
   - FK relationships: 2 min
   - API tests: 2 min

**Total**: ~45-60 minutes for complete deployment and data loading

---

## Contact Info

If issues arise during Mac Mini deployment:
- Check logs first: `docker logs <container_name>`
- Review `GADM_OPTIMIZATION_RESULTS.md` for common issues
- Check Flower UI for task states
- Compare with working laptop dev environment

---

## Success Criteria

✅ All 8 Docker containers running  
✅ 3 Celery workers showing as "ready"  
✅ Flower UI accessible at http://localhost:5555  
✅ GADM data loaded (~400K total records across 6 layers)  
✅ ForeignKey relationships populated  
✅ API endpoints returning GeoJSON  
✅ No OOM errors in logs  

When all criteria met: **Production-ready geospatial API server** 🎉

