# Development Workflow

## Branch Strategy

`main` contains stable baseline documentation and completed work. Each implementation phase should be developed on its own branch and merged back through a pull request.

Recommended first branch:

```text
phase-1-project-foundation
```

## Phases

### Phase 1: Project Foundation

- FastAPI backend shell.
- Angular frontend shell.
- PostgreSQL and Redis services.
- Celery worker entrypoint.
- Docker Compose setup.
- Initial CI checks.

### Phase 2: Core Data Model

- Employees.
- Availability.
- Vacation and sick leave.
- Shift demand.
- Scheduling runs and generated shifts.

### Phase 3: Google Sheets Integration

- Service account authentication.
- Sheet reader.
- Parser and mapper.
- Basic import validation.
- Persist valid availability and absence records.

### Phase 4: Scheduling Engine

- OR-Tools input model.
- Hard constraints.
- Soft constraints.
- Fairness objectives.
- Result persistence.

### Phase 5: Analytics Dashboard

- Workload analysis.
- Availability overview.
- Shift coverage.
- Weekly generated schedule.

### Phase 6: Testing and CI Hardening

- Backend tests with pytest.
- Scheduling-engine tests.
- Playwright end-to-end tests.
- GitHub Actions workflows.

## Local Google Sheets Smoke Test

This test verifies the Docker backend can read availability from Google Sheets and store it in PostgreSQL.

Keep the local credentials file out of Git. The `.env` value should point to the host machine path:

```env
GOOGLE_APPLICATION_CREDENTIALS=D:/path/to/google-credentials.local.json
```

Start the backend with the Google Sheets override:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml up -d --build backend
```

Run migrations:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml exec backend alembic upgrade head
```

Preview the sheet before importing:

```powershell
$weekStart = "2026-06-01"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/google-sheets/availability/preview?week_start=$weekStart" | ConvertTo-Json -Depth 10
```

Import the sheet when the preview has no errors:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/google-sheets/availability/import?week_start=$weekStart" | ConvertTo-Json -Depth 10
```

Check stored data:

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/employees" | ConvertTo-Json -Depth 10
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/availability?week_start=$weekStart" | ConvertTo-Json -Depth 10
```
