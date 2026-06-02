from datetime import date, time

from pydantic import BaseModel

from app.db.enums import AvailabilityType
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
