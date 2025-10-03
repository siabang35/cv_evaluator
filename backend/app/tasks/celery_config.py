from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Initialize Celery app
celery_app = Celery(
    'cv_evaluator',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.evaluation_tasks', 'app.tasks.cleanup_tasks']
)

# Celery configuration
celery_app.conf.update(
    # Serialization
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    
    # Timezone
    timezone='UTC',
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=1800,  # 30 minutes hard limit
    task_soft_time_limit=1500,  # 25 minutes soft limit
    
    # Result backend
    result_expires=86400,  # Results expire after 24 hours
    result_backend_transport_options={
        'master_name': 'mymaster',
        'visibility_timeout': 3600,
    },
    
    # Worker
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    
    # Retry policy
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    
    # Beat schedule for periodic tasks
    beat_schedule={
        'cleanup-old-jobs': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_jobs',
            'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
        },
        'cleanup-old-documents': {
            'task': 'app.tasks.cleanup_tasks.cleanup_old_documents',
            'schedule': crontab(hour=3, minute=0),  # Run daily at 3 AM
        },
    },
)

# Task routes
celery_app.conf.task_routes = {
    'app.tasks.evaluation_tasks.*': {'queue': 'evaluation'},
    'app.tasks.cleanup_tasks.*': {'queue': 'cleanup'},
}
