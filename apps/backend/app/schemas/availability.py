from datetime import date, time

from pydantic import BaseModel

from app.db.enums import AvailabilityType
from app.services.availability_analysis import AvailabilitySummary
from app.services.availability_queries import AvailabilityListItem


class AvailabilityResponse(BaseModel):
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    work_date: date
    start_time: time | None
    end_time: time | None
    availability_type: AvailabilityType
    notes: str | None


class AvailabilityWeekResponse(BaseModel):
    week_start: date
    week_end: date
    rows: list[AvailabilityResponse]
    row_count: int


class AvailabilityDaySummaryResponse(BaseModel):
    weekday: str
    work_date: date
    available_employee_count: int
    unavailable_employee_count: int
    available_hours: float


class AvailabilityEmployeeSummaryResponse(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str
    available_hours: float


class AvailabilitySummaryResponse(BaseModel):
    week_start: date
    week_end: date
    days: list[AvailabilityDaySummaryResponse]
    employees: list[AvailabilityEmployeeSummaryResponse]
    day_count: int
    employee_count: int


def build_availability_week_response(
    week_start: date,
    week_end: date,
    rows: list[AvailabilityListItem],
) -> AvailabilityWeekResponse:
    return AvailabilityWeekResponse(
        week_start=week_start,
        week_end=week_end,
        rows=[
            AvailabilityResponse.model_validate(row, from_attributes=True)
            for row in rows
        ],
        row_count=len(rows),
    )


def build_availability_summary_response(
    summary: AvailabilitySummary,
) -> AvailabilitySummaryResponse:
    return AvailabilitySummaryResponse(
        week_start=summary.week_start,
        week_end=summary.week_end,
        days=[
            AvailabilityDaySummaryResponse.model_validate(day, from_attributes=True)
            for day in summary.days
        ],
        employees=[
            AvailabilityEmployeeSummaryResponse.model_validate(employee, from_attributes=True)
            for employee in summary.employees
        ],
        day_count=len(summary.days),
        employee_count=len(summary.employees),
    )
