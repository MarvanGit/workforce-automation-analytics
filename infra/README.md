# Infrastructure

Local service orchestration for the workforce analytics platform.

## Services

- `backend`: FastAPI API on port `8000`
- `postgres`: PostgreSQL on port `5432`
- `redis`: Redis on port `6379`

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
