# Mac Mini Quick Reference

**IP**: 207.254.39.238  
**User**: Administrator  
**Password**: See `docs/notes/credentials_for_mac_mini.md`  
**Storage**: 1.5TB free

---

## Quick Connect

### SSH
```bash
ssh Administrator@207.254.39.238
# Password: 111222
```

### VNC (Screen Sharing)
```bash
# In Safari or terminal:
open vnc://207.254.39.238
# Password: 111222
```

### Reboot (If Needed)
- URL: https://macstadium.com
- User: erik@erikswedberg.com  
- Password: pRFGl@3Fk9bn!6US

---

## Project Location

**Standard location**: `~/work/`

Current deployment will be at:
```bash
~/work/geodjango_simple_template/
```

---

## Automated Deployment

### From Your Mac Laptop
```bash
# Run the deployment script
cd /path/to/geodjango_simple_template
./DEPLOY_TO_MAC_MINI.sh

# This will:
# 1. Test connection
# 2. Clone/update repo
# 3. Build images
# 4. Start all services
# 5. Run migrations
```

### Manual Deployment
```bash
# 1. SSH in
ssh Administrator@207.254.39.238

# 2. Clone repo
cd ~/work
git clone git@github.com:siege-analytics/geodjango_simple_template.git
cd geodjango_simple_template

# 3. Build and start
make build
make up

# 4. Load GADM
docker exec geodjango_webserver sh -c "cd /usr/src/app/hellodjango && python -c '
import os, django
os.environ.setdefault(\"DJANGO_SETTINGS_MODULE\", \"hellodjango.settings\")
django.setup()
from locations.tasks import load_gadm_pipelined
result = load_gadm_pipelined.delay()
print(f\"Task: {result.id}\")
print(\"Monitor: http://207.254.39.238:5555\")
'"
```

---

## Service Access

### From Browser
- **Django API**: http://207.254.39.238:8000
- **Nginx**: http://207.254.39.238:8001
- **Flower (Celery)**: http://207.254.39.238:5555
- **Admin**: http://207.254.39.238:8000/admin/

### From Command Line
```bash
# Check services
ssh Administrator@207.254.39.238 "docker ps"

# Check logs
ssh Administrator@207.254.39.238 "docker logs geodjango_celery_1"

# Shell into container
ssh Administrator@207.254.39.238
cd ~/work/geodjango_simple_template
make shell
```

---

## Docker Configuration

### Recommended Settings
```
Memory: 12GB
CPUs: 4-6 (use available cores)
Swap: 2GB
Disk: 100GB+
```

### Check Current Settings
```bash
ssh Administrator@207.254.39.238 "docker info | grep -E 'Memory|CPUs'"
```

### Change Settings
1. VNC into Mac Mini: `open vnc://207.254.39.238`
2. Open Docker Desktop
3. Settings → Resources
4. Adjust Memory/CPU sliders
5. Apply & Restart

---

## TODO: Security Hardening

Per Erik's notes, need to:
- [ ] Lock down ports 5432 and 5433 (PostgreSQL)
- [ ] Configure nginx to serve astralspace.dev properly
- [ ] Set up firewall rules
- [ ] Change default passwords in production
- [ ] Set `DEBUG=0` in production environment

---

## Monitoring Commands

### Quick Health Check
```bash
# From laptop
ssh Administrator@207.254.39.238 "cd ~/work/geodjango_simple_template && docker ps && echo '' && docker exec geodjango_celery_1 /opt/venv/bin/celery -A hellodjango inspect active"
```

### Check GADM Load Progress
```bash
# From laptop - check Flower
open http://207.254.39.238:5555

# Or SSH and check logs
ssh Administrator@207.254.39.238
docker logs -f geodjango_celery_1
```

### Check Data Loaded
```bash
ssh Administrator@207.254.39.238
docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c "
SELECT 
    'Admin_Level_0' as level, COUNT(*) as records 
FROM locations_admin_level_0
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
```

---

## Expected Results

### After Successful GADM Load
- **Admin_Level_0**: 263 countries
- **Admin_Level_1**: ~50,000 states/provinces
- **Admin_Level_2**: ~144,000 counties
- **Admin_Level_3**: ~144,000 
- **Admin_Level_4**: ~80,000
- **Admin_Level_5**: ~51,000

**Total**: ~400,000 administrative boundary records

### API Endpoints
```bash
# Test from laptop
curl http://207.254.39.238:8000/locations/admin_level_0s/ | jq '.results | length'
curl http://207.254.39.238:8000/locations/admin_level_1s/ | jq '.results | length'
```

---

## Troubleshooting

### Can't Connect
```bash
# Test connection
ping 207.254.39.238
ssh -v Administrator@207.254.39.238

# If Mac Mini is down, reboot via MacStadium portal
# URL: https://macstadium.com
```

### Services Not Starting
```bash
# SSH in and check
ssh Administrator@207.254.39.238
cd ~/work/geodjango_simple_template
docker ps -a  # See all containers, including stopped ones
docker logs geodjango_webserver  # Check for errors
```

### OOM on Mac Mini Too
```bash
# Reduce to 2 workers
# Edit compose.yaml, comment out celery_3 service
# Or use sequential loading (slower but stable)
```

---

## Notes from Erik

- GitLab: @erikswedberg
- Standard project location: `~/work/`
- Port security: Need to firewall 5432, 5433
- Domain config: astralspace.dev needs nginx configuration
- Storage: 1.5TB free (1.9TB if cleanup needed)

---

## Quick Deploy (One Command)

From your laptop:
```bash
cd /path/to/geodjango_simple_template
./DEPLOY_TO_MAC_MINI.sh
```

This automated script will handle everything!

