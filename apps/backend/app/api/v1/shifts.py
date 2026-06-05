from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.shifts import (
    ShiftDemandWeekResponse,
    ShiftTemplatesResponse,
    build_shift_demand_week_response,
    build_shift_templates_response,
)
from app.services.shift_queries import list_shift_templates, list_week_shift_demand

router = APIRouter(tags=["shifts"])
DB_SESSION = Depends(get_db)


@router.get("/shift-templates", response_model=ShiftTemplatesResponse)
async def get_shift_templates(
    db: AsyncSession = DB_SESSION,
) -> ShiftTemplatesResponse:
    templates = await list_shift_templates(db)
    return build_shift_templates_response(templates)


@router.get("/shift-demand", response_model=ShiftDemandWeekResponse)
async def get_shift_demand(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> ShiftDemandWeekResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_shift_demand(db, week_start)
    return build_shift_demand_week_response(week_start, rows)
