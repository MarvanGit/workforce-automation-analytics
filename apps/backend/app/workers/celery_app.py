from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "workforce_analytics",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.tasks.health"],
)

celery_app.conf.update(
    accept_content=["json"],
    enable_utc=True,
    result_serializer="json",
    task_default_queue="default",
    task_serializer="json",
    timezone="UTC",
)
