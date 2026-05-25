from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.health import HealthResponse

# Router for health check endpoints
router = APIRouter(tags=["health"])

# Endpoint for health check
@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.environment,
    )

