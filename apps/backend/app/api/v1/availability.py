from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.availability import (
    AvailabilitySummaryResponse,
    AvailabilityWeekResponse,
    build_availability_summary_response,
    build_availability_week_response,
)
from app.services.availability_analysis import summarize_week_availability
from app.services.availability_queries import list_week_availability

router = APIRouter(prefix="/availability", tags=["availability"])
DB_SESSION = Depends(get_db)


@router.get("", response_model=AvailabilityWeekResponse)
async def get_week_availability(week_start: date, db: AsyncSession = DB_SESSION,) -> AvailabilityWeekResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_availability(db, week_start)
    week_end = week_start + timedelta(days=5)

    return build_availability_week_response(
        week_start=week_start,
        week_end=week_end,
        rows=rows,
    )


@router.get("/summary", response_model=AvailabilitySummaryResponse)
async def get_availability_summary(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> AvailabilitySummaryResponse:
    
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_availability(db, week_start)
    summary = summarize_week_availability(rows, week_start)
    return build_availability_summary_response(summary)
