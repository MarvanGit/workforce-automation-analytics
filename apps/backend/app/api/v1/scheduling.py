from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.scheduling import (
    SchedulePreviewResponse,
    build_schedule_preview_response,
)
from app.services.absence_queries import list_week_absences
from app.services.availability_queries import list_week_availability
from app.services.scheduling_preview import build_schedule_preview
from app.services.shift_queries import list_week_shift_demand

router = APIRouter(prefix="/scheduling", tags=["scheduling"])
DB_SESSION = Depends(get_db)


@router.get("/preview", response_model=SchedulePreviewResponse)
async def get_schedule_preview(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> SchedulePreviewResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    availability_rows = await list_week_availability(db, week_start)
    absence_rows = await list_week_absences(db, week_start)
    demand_rows = await list_week_shift_demand(db, week_start)

    preview = build_schedule_preview(
        week_start=week_start,
        availability_rows=availability_rows,
        absence_rows=absence_rows,
        demand_rows=demand_rows,
    )
    return build_schedule_preview_response(preview)
