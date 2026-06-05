# Scheduling Workflow Smoke Test

This smoke test checks the full backend scheduling path against the local Docker backend and PostgreSQL database.

It calls the API in this order:

```text
health check
import Google Sheets availability
create shift template
create shift demand
preview schedule
save schedule run
read saved schedule run
```

## Prerequisites

Start the Docker backend with the Google Sheets override:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml up -d --build backend
```

Run migrations:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml exec backend alembic upgrade head
```

Your `.env` file must contain the Google Sheets values:

```env
GOOGLE_SHEETS_SPREADSHEET_ID=
GOOGLE_SHEETS_AVAILABILITY_RANGE=Availability!A:H
GOOGLE_APPLICATION_CREDENTIALS=
```

Do not commit `.env` or Google credentials files.

## Run The Smoke Test

From the project root:

```powershell
.\scripts\smoke-test-scheduling-workflow.ps1 -WeekStart "2026-06-08"
```

`WeekStart` must be a Monday. The backend uses it as the real date for the Monday-Saturday sheet columns.

By default, the script creates one `09:00-17:00` shift on Monday and asks for one employee.

## Useful Options

Use a different shift:

```powershell
.\scripts\smoke-test-scheduling-workflow.ps1 -WeekStart "2026-06-08" -ShiftStart "10:00" -ShiftEnd "18:00"
```

Ask for more employees:

```powershell
.\scripts\smoke-test-scheduling-workflow.ps1 -WeekStart "2026-06-08" -RequiredEmployeeCount 2
```

Skip Google Sheets import if availability is already stored:

```powershell
.\scripts\smoke-test-scheduling-workflow.ps1 -WeekStart "2026-06-08" -SkipImport
```

## Expected Result

The script should print JSON responses for each step. The final step should show a saved schedule run ID:

```text
Saved schedule run id: ...
```

If the preview has warnings, that does not always mean the API is broken. It can also mean the current availability does not fully cover the shift demand.

## Troubleshooting

If the script says a scheduling route is missing, rebuild the backend container:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml -f infra/docker-compose.google-sheets.yml up -d --build backend
```

This usually means Docker is still running an older backend image that does not include the latest shift or scheduling endpoints.

If PowerShell blocks the script because of execution policy, run it like this:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\smoke-test-scheduling-workflow.ps1 -WeekStart "2026-06-08"
```
