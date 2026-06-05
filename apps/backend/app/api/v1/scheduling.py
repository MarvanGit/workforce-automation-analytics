from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.scheduling import (
    SavedScheduleRunResponse,
    SchedulePreviewResponse,
    ScheduleRunsResponse,
    build_saved_schedule_run_response,
    build_schedule_preview_response,
    build_schedule_runs_response,
)
from app.services.absence_queries import list_week_absences
from app.services.availability_queries import list_week_availability
from app.services.scheduling_preview import build_schedule_preview
from app.services.scheduling_queries import get_schedule_run, list_schedule_runs
from app.services.scheduling_storage import save_schedule_preview
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


@router.post(
    "/runs",
    response_model=SavedScheduleRunResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_schedule_run(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> SavedScheduleRunResponse:
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
    saved_run = await save_schedule_preview(db, preview)
    return build_saved_schedule_run_response(saved_run)


@router.get("/runs", response_model=ScheduleRunsResponse)
async def get_schedule_runs(
    db: AsyncSession = DB_SESSION,
) -> ScheduleRunsResponse:
    runs = await list_schedule_runs(db)
    return build_schedule_runs_response(runs)


@router.get("/runs/{run_id}", response_model=SavedScheduleRunResponse)
async def get_schedule_run_by_id(
    run_id: str,
    db: AsyncSession = DB_SESSION,
) -> SavedScheduleRunResponse:
    saved_run = await get_schedule_run(db, run_id)
    if saved_run is None:
        raise HTTPException(status_code=404, detail="Schedule run was not found.")

    return build_saved_schedule_run_response(saved_run)
