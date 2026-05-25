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
