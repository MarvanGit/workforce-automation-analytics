from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.shifts import (
    ShiftDemandCreateRequest,
    ShiftDemandResponse,
    ShiftDemandWeekResponse,
    ShiftTemplateCreateRequest,
    ShiftTemplateResponse,
    ShiftTemplatesResponse,
    build_shift_demand_response,
    build_shift_demand_week_response,
    build_shift_template_response,
    build_shift_templates_response,
)
from app.services.shift_queries import list_shift_templates, list_week_shift_demand
from app.services.shift_storage import (
    create_shift_demand,
    create_shift_template,
    delete_shift_demand,
)

router = APIRouter(tags=["shifts"])
DB_SESSION = Depends(get_db)


@router.get("/shift-templates", response_model=ShiftTemplatesResponse)
async def get_shift_templates(
    db: AsyncSession = DB_SESSION,
) -> ShiftTemplatesResponse:
    templates = await list_shift_templates(db)
    return build_shift_templates_response(templates)


@router.post(
    "/shift-templates",
    response_model=ShiftTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_shift_template(
    payload: ShiftTemplateCreateRequest,
    db: AsyncSession = DB_SESSION,
) -> ShiftTemplateResponse:
    try:
        template = await create_shift_template(
            db,
            name=payload.name,
            start_time=payload.start_time,
            end_time=payload.end_time,
            active=payload.active,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return build_shift_template_response(template)


@router.get("/shift-demand", response_model=ShiftDemandWeekResponse)
async def get_shift_demand(
    week_start: date,
    db: AsyncSession = DB_SESSION,
) -> ShiftDemandWeekResponse:
    if week_start.weekday() != 0:
        raise HTTPException(status_code=400, detail="week_start must be a Monday.")

    rows = await list_week_shift_demand(db, week_start)
    return build_shift_demand_week_response(week_start, rows)


@router.post(
    "/shift-demand",
    response_model=ShiftDemandResponse,
    status_code=status.HTTP_201_CREATED,
)
async def post_shift_demand(
    payload: ShiftDemandCreateRequest,
    db: AsyncSession = DB_SESSION,
) -> ShiftDemandResponse:
    try:
        row = await create_shift_demand(
            db,
            demand_date=payload.demand_date,
            shift_template_id=payload.shift_template_id,
            required_employee_count=payload.required_employee_count,
            notes=payload.notes,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return build_shift_demand_response(row)


@router.delete("/shift-demand/{demand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift_demand_row(
    demand_id: str,
    db: AsyncSession = DB_SESSION,
) -> None:
    deleted = await delete_shift_demand(db, demand_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="shift demand was not found.")
