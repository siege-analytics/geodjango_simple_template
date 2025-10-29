# GeoDjango Simple Template Documentation

## Overview

GeoDjango Simple Template is a streamlined Django application template with geospatial capabilities. It provides a clean, production-ready foundation for building geospatial web applications without the complexity of a full data warehouse.

## Architecture

### Core Components

1. **Django 4.2+ with GeoDjango**
   - Web framework with geospatial extensions
   - Built-in support for PostGIS
   - Admin interface for data management

2. **PostGIS 16.2**
   - Geospatial database extension
   - Spatial data types and functions
   - Geographic information system capabilities

3. **Nginx**
   - Reverse proxy and static file serving
   - Production-ready web server
   - SSL termination support

4. **Gunicorn**
   - WSGI HTTP server for Django
   - Production-grade application server
   - Process management and monitoring

### Service Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Nginx      │    │   Django App    │    │     PostGIS     │
│   (Port 1337)   │◄──►│   (Port 8000)   │◄──►│   (Port 54321)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Configuration

### Environment Variables

The system uses environment variables for configuration:

```bash
# Django Configuration
DEBUG=1
SECRET_KEY=your_secret_key_here
DJANGO_ALLOWED_HOSTS="*"

# Database Configuration
SQL_ENGINE=django.contrib.gis.db.backends.postgis
SQL_HOST=postgis
SQL_DATABASE=geodjango_database
SQL_USER=dheerajchand
SQL_PASSWORD=strongpasswd
SQL_PORT=5432

# Gunicorn Configuration
GUNICORN_HOST=0.0.0.0
GUNICORN_PORT=8000
GUNICORN_WORKERS=4
GUNICORN_TIMEOUT=120
```

### Database Configuration

Default PostgreSQL/PostGIS setup:
- **Database**: `geodjango_database`
- **User**: `dheerajchand`
- **Password**: `strongpasswd`
- **Port**: `54321`

## Quick Start

### Prerequisites

- Docker Desktop
- Git

### Setup

1. **Clone and Setup**
   ```bash
   git clone <repository>
   cd geodjango_simple_template
   ```

2. **Start Services**
   ```bash
   docker compose up -d
   ```

3. **Run Migrations**
   ```bash
   docker exec geodjango_webserver python manage.py migrate
   ```

4. **Create Superuser**
   ```bash
   docker exec -it geodjango_webserver python manage.py createsuperuser
   ```

### Access Points

- **Application**: http://localhost:1337
- **Django Admin**: http://localhost:1337/admin
- **PostGIS**: localhost:54321

## Usage Examples

### Django Models with Geospatial Data

```python
from django.contrib.gis.db import models

class Location(models.Model):
    name = models.CharField(max_length=100)
    point = models.PointField()
    polygon = models.PolygonField(null=True, blank=True)
    
    def __str__(self):
        return self.name
```

### Spatial Queries

```python
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance

# Find locations within 10km of a point
center = Point(-122.4194, 37.7749)  # San Francisco
nearby = Location.objects.filter(
    point__distance_lte=(center, Distance(km=10))
)
```

### API Endpoints

```python
from django.contrib.gis.geos import Point
from rest_framework import viewsets
from rest_framework.response import Response

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    
    def list(self, request):
        # Add spatial filtering logic
        return Response(self.get_queryset().values())
```

## Development

### Project Structure

```
geodjango_simple_template/
├── app/
│   ├── hellodjango/
│   │   ├── settings/
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── locations/
│   │   ├── models/
│   │   ├── views/
│   │   └── serializers/
│   └── manage.py
├── docker/
│   ├── Dockerfile
│   └── nginx/
├── compose.yaml
└── README.md
```

### Adding New Apps

1. Create new Django app:
   ```bash
   docker exec geodjango_webserver python manage.py startapp myapp
   ```

2. Add to `INSTALLED_APPS` in settings
3. Create models, views, and URLs
4. Run migrations

### Custom Models

```python
from django.contrib.gis.db import models

class MySpatialModel(models.Model):
    name = models.CharField(max_length=100)
    geometry = models.GeometryField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'my_spatial_model'
```

## Deployment

### Production Configuration

1. **Environment Variables**
   ```bash
   DEBUG=0
   SECRET_KEY=your_production_secret_key
   DJANGO_ALLOWED_HOSTS=yourdomain.com
   ```

2. **SSL Configuration**
   - Add SSL certificates to nginx
   - Update nginx configuration for HTTPS
   - Set secure cookie settings

3. **Database Security**
   - Change default passwords
   - Use strong authentication
   - Enable SSL connections

### Scaling

- Use multiple Gunicorn workers
- Add load balancer for multiple instances
- Use external database for production
- Implement caching with Redis

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostGIS container is running
   - Verify database credentials
   - Check network connectivity

2. **Static Files Not Loading**
   - Run `collectstatic` command
   - Check nginx configuration
   - Verify volume mounts

3. **Geospatial Data Issues**
   - Ensure PostGIS extension is enabled
   - Check SRID (Spatial Reference System)
   - Verify geometry data format

### Debugging

```bash
# Check container logs
docker logs geodjango_webserver
docker logs geodjango_postgis
docker logs geodjango_nginx

# Access Django shell
docker exec -it geodjango_webserver python manage.py shell

# Check database
docker exec -it geodjango_postgis psql -U dheerajchand -d geodjango_database
```

## Performance Optimization

### Database Optimization

- Add spatial indexes for geometry fields
- Use database connection pooling
- Optimize spatial queries
- Regular VACUUM and ANALYZE

### Application Optimization

- Use Django's select_related and prefetch_related
- Implement caching for expensive queries
- Use database views for complex spatial operations
- Optimize static file serving

### Nginx Optimization

- Enable gzip compression
- Set appropriate cache headers
- Use CDN for static assets
- Configure rate limiting

## Security

### Django Security

- Use strong SECRET_KEY
- Set DEBUG=False in production
- Configure ALLOWED_HOSTS properly
- Use HTTPS in production

### Database Security

- Change default passwords
- Use database users with minimal privileges
- Enable SSL connections
- Regular security updates

### Container Security

- Use non-root users in containers
- Keep base images updated
- Scan for vulnerabilities
- Use secrets management

## Monitoring

### Application Monitoring

- Django Debug Toolbar for development
- Logging configuration for production
- Health check endpoints
- Performance monitoring

### Infrastructure Monitoring

- Container health checks
- Resource usage monitoring
- Database performance metrics
- Network connectivity monitoring

## Contributing

### Development Setup

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

### Code Standards

- Follow Django coding standards
- Use type hints where appropriate
- Write tests for new features
- Update documentation

### Testing

```bash
# Run tests
docker exec geodjango_webserver python manage.py test

# Run with coverage
docker exec geodjango_webserver coverage run --source='.' manage.py test
docker exec geodjango_webserver coverage report
```

## License

[Add license information]

## Support

[Add support contact information]



