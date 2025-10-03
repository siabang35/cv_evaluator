#!/bin/bash

# Start Celery worker with proper configuration
celery -A app.tasks.celery_config worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --time-limit=1800 \
    --soft-time-limit=1500 \
    -Q evaluation,cleanup
