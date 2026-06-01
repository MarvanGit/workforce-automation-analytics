# Database Migrations

Alembic migration files live in `versions/`.

Generate a migration after changing SQLAlchemy models:

```powershell
uv run alembic revision --autogenerate -m "describe change"
```

Apply migrations:

```powershell
uv run alembic upgrade head
```

`env.py` reads `DATABASE_URL` from the backend settings, so local migration commands should be run with a populated `.env`.

