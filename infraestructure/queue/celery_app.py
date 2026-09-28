"""
Celery application configuration.

Defines the Celery app with Redis as broker and result backend.
Includes beat schedule for periodic tasks.
"""

from celery import Celery
from celery.schedules import crontab

from core.config import settings


celery_app = Celery(
    "tapi",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Task routing
    task_routes={
        "infraestructure.queue.tasks.review_tasks.*": {"queue": "reviews"},
        "infraestructure.queue.tasks.notification_tasks.*": {"queue": "notifications"},
        "infraestructure.queue.tasks.google_maps_tasks.*": {"queue": "google"},
    },

    # Beat schedule — periodic tasks
    beat_schedule={
        "process-offline-reviews": {
            "task": "infraestructure.queue.tasks.review_tasks.process_offline_queue",
            "schedule": crontab(minute="0", hour="*/1"),  # Every hour
            "args": (),
        },
        "process-google-reviews": {
            "task": "infraestructure.queue.tasks.google_maps_tasks.push_pending_reviews",
            "schedule": crontab(minute="*/15"),  # Every 15 minutes
            "args": (),
        },
    },
)

# Auto-discover tasks in the tasks subpackage
celery_app.autodiscover_tasks(
    [
        "infraestructure.queue.tasks",
    ]
)
