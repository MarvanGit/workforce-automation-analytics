# Workforce Automation Analytics

Full-stack workforce analytics and scheduling platform for importing employee availability, validating planning data, optimizing schedules, and analyzing workload and conflicts.

## Planned Stack

- Backend: Python, FastAPI, PostgreSQL
- Background jobs: Celery, Redis
- Optimization: Google OR-Tools
- Frontend: Angular
- Data import: Google Sheets API
- Testing: pytest, Playwright
- Delivery: Docker, GitHub Actions

## Repository Intent

The `main` branch starts with project structure and architecture documentation only. Implementation work should happen in feature branches, beginning with Phase 1.

## Planned Layout

```text
apps/backend      FastAPI backend, scheduling engine, workers
apps/frontend     Angular dashboard
infra             Docker and service infrastructure
docs              Architecture and workflow documentation
scripts           Developer automation scripts
```

## Development Flow

1. Keep `main` stable and documentation-first.
2. Create a branch for each implementation phase.
3. Open pull requests back into `main`.
4. Add tests and CI as the implementation appears.

## Local Infrastructure

Start the current backend infrastructure stack:

```powershell
Copy-Item .env.example .env
docker compose -f infra/docker-compose.yml up --build
```

Backend health check:

```text
http://localhost:8000/api/v1/health
```

Frontend:

```text
http://localhost:4200
```

Worker ping check:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml exec backend python -c "from app.workers.tasks.health import ping; print(ping.delay().get(timeout=10))"
```

## CI Checks

GitHub Actions runs focused checks for each project area:

- Backend: `uv sync`, `ruff`, and `pytest`
- Frontend: `npm ci`, Angular build, and spec TypeScript checks
- Infrastructure: Docker Compose configuration validation
