from datetime import date, time, timedelta

from pydantic import BaseModel

from app.db.models import ShiftTemplate
from app.services.shift_queries import ShiftDemandListItem

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]


class ShiftTemplateResponse(BaseModel):
    id: str
    name: str
    start_time: time
    end_time: time
    duration_minutes: int
    is_overnight: bool
    active: bool


class ShiftTemplatesResponse(BaseModel):
    rows: list[ShiftTemplateResponse]
    row_count: int


class ShiftTemplateCreateRequest(BaseModel):
    name: str
    start_time: time
    end_time: time
    active: bool = True


class ShiftDemandResponse(BaseModel):
    id: str
    demand_date: date
    weekday: str
    shift_template_id: str
    shift_template_name: str
    shift_start_time: time
    shift_end_time: time
    required_employee_count: int
    notes: str | None


class ShiftDemandWeekResponse(BaseModel):
    week_start: date
    week_end: date
    rows: list[ShiftDemandResponse]
    row_count: int


class ShiftDemandCreateRequest(BaseModel):
    demand_date: date
    shift_template_id: str
    required_employee_count: int
    notes: str | None = None


def build_shift_template_response(
    template: ShiftTemplate,
) -> ShiftTemplateResponse:
    return ShiftTemplateResponse.model_validate(template, from_attributes=True)


def build_shift_templates_response(
    templates: list[ShiftTemplate],
) -> ShiftTemplatesResponse:
    return ShiftTemplatesResponse(
        rows=[
            ShiftTemplateResponse.model_validate(template, from_attributes=True)
            for template in templates
        ],
        row_count=len(templates),
    )


def build_shift_demand_week_response(
    week_start: date,
    rows: list[ShiftDemandListItem],
) -> ShiftDemandWeekResponse:
    week_end = week_start + timedelta(days=5)

    return ShiftDemandWeekResponse(
        week_start=week_start,
        week_end=week_end,
        rows=[build_shift_demand_response(row) for row in rows],
        row_count=len(rows),
    )


def build_shift_demand_response(row: ShiftDemandListItem) -> ShiftDemandResponse:
    return ShiftDemandResponse(
        id=row.id,
        demand_date=row.demand_date,
        weekday=WEEKDAY_NAMES[row.demand_date.weekday()],
        shift_template_id=row.shift_template_id,
        shift_template_name=row.shift_template_name,
        shift_start_time=row.shift_start_time,
        shift_end_time=row.shift_end_time,
        required_employee_count=row.required_employee_count,
        notes=row.notes,
    )
