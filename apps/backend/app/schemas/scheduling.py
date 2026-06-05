from datetime import date, time

from pydantic import BaseModel

from app.services.scheduling_preview import SchedulePreview


class ScheduleEmployeePreviewResponse(BaseModel):
    employee_id: str
    employee_code: str
    employee_name: str


class ScheduleShiftPreviewResponse(BaseModel):
    demand_id: str
    demand_date: date
    weekday: str
    shift_template_id: str
    shift_template_name: str
    shift_start_time: time
    shift_end_time: time
    required_employee_count: int
    assigned_employees: list[ScheduleEmployeePreviewResponse]
    missing_employee_count: int


class SchedulePreviewResponse(BaseModel):
    week_start: date
    week_end: date
    shifts: list[ScheduleShiftPreviewResponse]
    shift_count: int
    assignment_count: int
    warnings: list[str]
    warning_count: int


def build_schedule_preview_response(
    preview: SchedulePreview,
) -> SchedulePreviewResponse:
    assignment_count = sum(len(shift.assigned_employees) for shift in preview.shifts)

    return SchedulePreviewResponse(
        week_start=preview.week_start,
        week_end=preview.week_end,
        shifts=[
            ScheduleShiftPreviewResponse.model_validate(shift, from_attributes=True)
            for shift in preview.shifts
        ],
        shift_count=len(preview.shifts),
        assignment_count=assignment_count,
        warnings=preview.warnings,
        warning_count=len(preview.warnings),
    )
