from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.absences import AbsenceWeekResponse, build_absence_week_response
from app.services.absence_queries import list_week_absences

router = APIRouter(prefix="/absences", tags=["absences"])
DB_SESSION = Depends(get_db)


@router.get("", response_model=AbsenceWeekResponse)
async def get_week_absences(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> AbsenceWeekResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_absences(db, week_start)
    return build_absence_week_response(week_start, rows)
