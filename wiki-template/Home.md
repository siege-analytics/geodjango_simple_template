# ${PROJECT_NAME} - GeoDjango Application

## Overview

${PROJECT_NAME} is a streamlined Django application with geospatial capabilities. It provides a clean, production-ready foundation for building geospatial web applications.

## Quick Start

### Prerequisites
- Docker Desktop
- Git

### Setup
```bash
git clone <your-repository-url>
cd ${PROJECT_NAME}
docker compose up -d
```

### Initial Configuration
```bash
# Run migrations
docker exec ${PROJECT_PREFIX}_webserver python manage.py migrate

# Create superuser
docker exec -it ${PROJECT_PREFIX}_webserver python manage.py createsuperuser
```

## Services

| Service | URL | Description |
|---------|-----|-------------|
| Application | http://localhost:${DJANGO_PORT} | Main Django application |
| Django Admin | http://localhost:${DJANGO_PORT}/admin | Admin interface |
| PostGIS | localhost:${POSTGRES_PORT} | Geospatial database |

## Configuration

### Environment Variables
```bash
PROJECT_NAME=${PROJECT_NAME}
PROJECT_PREFIX=${PROJECT_PREFIX}
POSTGRES_USER=${POSTGRES_USER}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=${POSTGRES_DB}
POSTGRES_PORT=${POSTGRES_PORT}
DJANGO_PORT=${DJANGO_PORT}
```

### Database Configuration
- **Database**: ${POSTGRES_DB}
- **User**: ${POSTGRES_USER}
- **Password**: ${POSTGRES_PASSWORD}
- **Port**: ${POSTGRES_PORT}

## Documentation

- [Complete Documentation](DOCUMENTATION.md)
- [Configuration Guide](DOCUMENTATION.md#configuration)
- [Deployment Guide](DOCUMENTATION.md#deployment)
- [Troubleshooting](DOCUMENTATION.md#troubleshooting)

## Support

For issues and questions:
1. Check the [troubleshooting guide](DOCUMENTATION.md#troubleshooting)
2. Review [common issues](DOCUMENTATION.md#common-issues)
3. Open an issue in the repository

## License

[Add your license information]
