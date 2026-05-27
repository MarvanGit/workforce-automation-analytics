from app.workers.celery_app import celery_app


@celery_app.task(name="app.workers.tasks.health.ping")
def ping() -> dict[str, str]:
    return {"status": "ok"}

