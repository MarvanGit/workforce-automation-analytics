from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.availability import (
    AvailabilityWeekResponse,
    build_availability_week_response,
)
from app.services.availability_queries import list_week_availability

router = APIRouter(prefix="/availability", tags=["availability"])
DB_SESSION = Depends(get_db)


@router.get("", response_model=AvailabilityWeekResponse)
async def get_week_availability(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> AvailabilityWeekResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_availability(db, week_start)
    week_end = week_start + timedelta(days=5)

    return build_availability_week_response(
        week_start=week_start,
        week_end=week_end,
        rows=rows,
    )
