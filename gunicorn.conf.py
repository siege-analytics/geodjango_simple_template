# Gunicorn config for the GeoDjango template.
#
# Workers: (2 * cpu) + 1 is the gunicorn-recommended baseline for CPU-bound
# work. GeoDjango views frequently spend time inside libgeos / libgdal, so
# threads-per-worker is also useful — gthread workers give us per-worker
# concurrency without losing fork isolation.
#
# Most knobs are overridable via env vars so a downstream consumer can tune
# without forking this file.

import multiprocessing
import os


def _int(name, default):
    return int(os.getenv(name, str(default)))


# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
backlog = _int("GUNICORN_BACKLOG", 2048)

# Worker processes
workers = _int("GUNICORN_WORKERS", (2 * multiprocessing.cpu_count()) + 1)
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "gthread")
threads = _int("GUNICORN_THREADS", 4)
worker_connections = _int("GUNICORN_WORKER_CONNECTIONS", 1000)
timeout = _int("GUNICORN_TIMEOUT", 120)
graceful_timeout = _int("GUNICORN_GRACEFUL_TIMEOUT", 30)
keepalive = _int("GUNICORN_KEEPALIVE", 5)

# Recycle workers periodically to bound memory drift from GDAL/GEOS handles.
max_requests = _int("GUNICORN_MAX_REQUESTS", 1000)
max_requests_jitter = _int("GUNICORN_MAX_REQUESTS_JITTER", 100)

# /dev/shm is tmpfs in containers; keeps worker heartbeats off disk-backed FS.
worker_tmp_dir = os.getenv("GUNICORN_WORKER_TMP_DIR", "/dev/shm")

# Logging — stdout/stderr by default so docker / kubectl logs work.
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = (
    '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
)

# Process naming
proc_name = os.getenv("GUNICORN_PROC_NAME", "geodjango")
