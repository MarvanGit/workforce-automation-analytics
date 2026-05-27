from app.workers.celery_app import celery_app
from app.workers.tasks.health import ping


def test_celery_app_uses_configured_redis_urls() -> None:
    assert celery_app.conf.broker_url == "redis://redis:6379/0"
    assert celery_app.conf.result_backend == "redis://redis:6379/1"
    assert "app.workers.tasks.health" in celery_app.conf.include


def test_ping_task_runs_locally() -> None:
    result = ping.apply()

    assert result.successful()
    assert result.get() == {"status": "ok"}
