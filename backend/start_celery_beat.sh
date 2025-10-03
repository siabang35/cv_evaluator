#!/bin/bash

# Start Celery beat for periodic tasks
celery -A app.tasks.celery_config beat \
    --loglevel=info \
    --pidfile=/tmp/celerybeat.pid
