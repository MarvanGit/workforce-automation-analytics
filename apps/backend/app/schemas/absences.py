from datetime import date, timedelta

from pydantic import BaseModel

from app.db.enums import AbsenceType
from app.services.absence_queries import AbsenceListItem


class AbsenceResponse(BaseModel):
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    start_date: date
    end_date: date
    absence_type: AbsenceType
    notes: str | None


class AbsenceWeekResponse(BaseModel):
    week_start: date
    week_end: date
    rows: list[AbsenceResponse]
    row_count: int


def build_absence_week_response(
    week_start: date,
    rows: list[AbsenceListItem],
) -> AbsenceWeekResponse:
    return AbsenceWeekResponse(
        week_start=week_start,
        week_end=week_start + timedelta(days=5),
        rows=[
            AbsenceResponse.model_validate(row, from_attributes=True)
            for row in rows
        ],
        row_count=len(rows),
    )
