# Infrastructure

Local service orchestration for the workforce analytics platform.

## Services

- `backend`: FastAPI API on port `8000`
- `postgres`: PostgreSQL on port `5432`
- `redis`: Redis on port `6379`
- `worker`: Celery worker using Redis as broker/result backend

## Commands

Create your local environment file and fill in the blank secret values:

```powershell
Copy-Item .env.example .env
```

Start the stack:

```powershell
docker compose -f infra/docker-compose.yml up --build
```

Start in the background:

```powershell
docker compose -f infra/docker-compose.yml up --build -d
```

Stop the stack:

```powershell
docker compose -f infra/docker-compose.yml down
```

Check the backend:

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health
```

Check the worker ping task:

```powershell
docker compose --env-file .env -f infra/docker-compose.yml exec backend python -c "from app.workers.tasks.health import ping; print(ping.delay().get(timeout=10))"
```
