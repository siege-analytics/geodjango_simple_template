#!/bin/bash

# Deployment script for Mac Mini (207.254.39.238)
# Usage: ./DEPLOY_TO_MAC_MINI.sh

set -e  # Exit on error

echo "========================================"
echo "GeoDjango Deployment to Mac Mini"
echo "Target: Administrator@207.254.39.238"
echo "========================================"
echo ""

# Connection details
MAC_MINI_HOST="207.254.39.238"
MAC_MINI_USER="Administrator"
PROJECT_DIR="~/work/geodjango_simple_template"
REPO_URL="git@github.com:siege-analytics/geodjango_simple_template.git"

echo "📋 Pre-flight checks..."
echo ""

# Check if we can connect
echo "1. Testing SSH connection..."
ssh -o ConnectTimeout=5 ${MAC_MINI_USER}@${MAC_MINI_HOST} "echo '✅ SSH connection successful'" || {
    echo "❌ Cannot connect to Mac Mini"
    echo "Run: ssh ${MAC_MINI_USER}@${MAC_MINI_HOST}"
    echo "Password: (see credentials_for_mac_mini.md)"
    exit 1
}

echo "2. Checking Docker on Mac Mini..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "docker --version" || {
    echo "❌ Docker not found or not running on Mac Mini"
    echo "Please install/start Docker Desktop first"
    exit 1
}

echo "3. Checking Docker resources..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "docker info | grep -E 'Total Memory|CPUs'"

echo ""
echo "✅ Pre-flight checks passed!"
echo ""

# Deployment
echo "🚀 Starting deployment..."
echo ""

echo "Step 1: Clone/Update repository..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "
    cd ~/work || mkdir -p ~/work && cd ~/work
    
    if [ -d geodjango_simple_template ]; then
        echo '📦 Repository exists, updating...'
        cd geodjango_simple_template
        git pull origin main
    else
        echo '📦 Cloning repository...'
        git clone ${REPO_URL}
        cd geodjango_simple_template
    fi
    
    echo '✅ Repository ready'
    pwd
    git log -1 --oneline
"

echo ""
echo "Step 2: Build Docker images..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "
    cd ${PROJECT_DIR}
    make build
"

echo ""
echo "Step 3: Start services..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "
    cd ${PROJECT_DIR}
    make up
    sleep 10
    docker ps | grep geodjango
"

echo ""
echo "Step 4: Run migrations..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "
    cd ${PROJECT_DIR}
    docker exec geodjango_webserver sh -c 'cd /usr/src/app/hellodjango && python manage.py migrate'
"

echo ""
echo "Step 5: Verify gid_*_string columns..."
ssh ${MAC_MINI_USER}@${MAC_MINI_HOST} "
    docker exec geodjango_postgis psql -U dheerajchand -d geodjango_database -c '
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = '\"'locations_admin_level_1'\"' 
    AND column_name LIKE '\"'%string%'\"';
    '
"

echo ""
echo "========================================"
echo "✅ DEPLOYMENT COMPLETE"
echo "========================================"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. SSH to Mac Mini:"
echo "   ssh ${MAC_MINI_USER}@${MAC_MINI_HOST}"
echo ""
echo "2. Load GADM data:"
echo "   cd ${PROJECT_DIR}"
echo "   docker exec geodjango_webserver sh -c \"cd /usr/src/app/hellodjango && python -c '"
echo "   import os, django, time"
echo "   os.environ.setdefault(\\\"DJANGO_SETTINGS_MODULE\\\", \\\"hellodjango.settings\\\")"
echo "   django.setup()"
echo "   from locations.tasks import load_gadm_pipelined"
echo "   result = load_gadm_pipelined.delay()"
echo "   print(f\\\"Task ID: {result.id}\\\")"
echo "   '\""
echo ""
echo "3. Monitor with Flower:"
echo "   http://${MAC_MINI_HOST}:5555"
echo ""
echo "4. Or monitor logs:"
echo "   docker logs -f geodjango_celery_1"
echo ""
echo "Expected duration: 8-10 minutes for full GADM load"
echo ""

