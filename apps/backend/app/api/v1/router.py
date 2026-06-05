from fastapi import APIRouter

from app.api.v1.absences import router as absences_router
from app.api.v1.availability import router as availability_router
from app.api.v1.employees import router as employees_router
from app.api.v1.google_sheets import router as google_sheets_router
from app.api.v1.health import router as health_router
from app.api.v1.shifts import router as shifts_router

# Main API router that includes all sub-routers
api_router = APIRouter()
api_router.include_router(absences_router)
api_router.include_router(availability_router)
api_router.include_router(employees_router)
api_router.include_router(google_sheets_router)
api_router.include_router(health_router)
api_router.include_router(shifts_router)
