# Backend

FastAPI backend for the workforce analytics and scheduling platform.

## Local Commands

Install development dependencies from this directory:

```powershell
uv sync --dev
```

Run the API locally:

```powershell
uv run uvicorn app.main:app --reload
```

Run tests:

```powershell
uv run pytest
```

Initial health endpoint:

```text
GET /api/v1/health
```

Celery worker entrypoint:

```powershell
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO
```

Run database migrations:

```powershell
uv run alembic upgrade head
```

The migration command expects `DATABASE_URL` to be configured, either through `.env` or the current shell.
