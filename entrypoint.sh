#!/bin/bash
set -eu

API_HOST=0.0.0.0
API_PORT=${API_PORT:-5000}
API_WORKERS=${API_WORKERS:-3}
API_WORKER_MAX_REQUESTS=${API_WORKER_MAX_REQUESTS:-10000}
CELERY_WORKER_CONCURRENCY=${CELERY_WORKER_CONCURRENCY:-2}

case "$1" in
    api) poetry run gunicorn immuni_exposure_ingestion.sanic:sanic_app \
            --access-logfile='-' \
            --bind=${API_HOST}:${API_PORT} \
            --logger-class=immuni_common.helpers.logging.CustomGunicornLogger \
            --max-requests=${API_WORKER_MAX_REQUESTS} \
            --workers=${API_WORKERS} \
            --worker-class=immuni_common.uvicorn.ImmuniUvicornWorker ;;
    beat) poetry run celery beat \
            --app=immuni_exposure_ingestion.celery.celery_app \
            --loglevel=debug ;;
    worker) poetry run celery worker \
            --app=immuni_exposure_ingestion.celery.celery_app \
            --concurrency=${CELERY_WORKER_CONCURRENCY} \
            --task-events \
            --without-gossip \
            --without-mingle \
            --without-heartbeat \
            --loglevel=debug ;;
    debug) echo "Running in debug mode ..." \
            && tail -f /dev/null ;;  # Allow entering the container to inspect the environment.
    *) echo "Received unknown command $1 (allowed: api, beat, worker)"
       exit 2 ;;
esac



poetry run gunicorn immuni_exposure_ingestion.sanic:sanic_app \
            --access-logfile='-' \
            --bind=0.0.0.0:5001 \
            --logger-class=immuni_common.helpers.logging.CustomGunicornLogger \
            --max-requests=1000 \
            --workers=1 \
            --worker-class=immuni_common.uvicorn.ImmuniUvicornWorker