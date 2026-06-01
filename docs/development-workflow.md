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
