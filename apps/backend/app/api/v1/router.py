from fastapi import APIRouter

from app.api.v1.google_sheets import router as google_sheets_router
from app.api.v1.health import router as health_router

# Main API router that includes all sub-routers
api_router = APIRouter()
api_router.include_router(google_sheets_router)
api_router.include_router(health_router)
