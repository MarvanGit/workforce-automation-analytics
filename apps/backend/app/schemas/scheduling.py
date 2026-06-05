from datetime import date, datetime, time

from pydantic import BaseModel

from app.services.scheduling_preview import SchedulePreview
from app.services.scheduling_queries import ScheduleRunListItem
from app.services.scheduling_storage import SavedScheduleRun


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


class SavedScheduledShiftResponse(BaseModel):
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    shift_date: date
    shift_template_id: str
    shift_template_name: str
    start_datetime: datetime
    end_datetime: datetime


class SavedScheduleRunResponse(BaseModel):
    id: str
    start_date: date
    end_date: date
    status: str
    scheduled_shifts: list[SavedScheduledShiftResponse]
    scheduled_shift_count: int
    warnings: list[str]
    warning_count: int


class ScheduleRunSummaryResponse(BaseModel):
    id: str
    start_date: date
    end_date: date
    status: str


class ScheduleRunsResponse(BaseModel):
    rows: list[ScheduleRunSummaryResponse]
    row_count: int


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


def build_schedule_runs_response(
    runs: list[ScheduleRunListItem],
) -> ScheduleRunsResponse:
    return ScheduleRunsResponse(
        rows=[
            ScheduleRunSummaryResponse.model_validate(run, from_attributes=True)
            for run in runs
        ],
        row_count=len(runs),
    )


def build_saved_schedule_run_response(
    saved_run: SavedScheduleRun,
) -> SavedScheduleRunResponse:
    return SavedScheduleRunResponse(
        id=saved_run.id,
        start_date=saved_run.start_date,
        end_date=saved_run.end_date,
        status=saved_run.status,
        scheduled_shifts=[
            SavedScheduledShiftResponse.model_validate(shift, from_attributes=True)
            for shift in saved_run.scheduled_shifts
        ],
        scheduled_shift_count=len(saved_run.scheduled_shifts),
        warnings=saved_run.warnings,
        warning_count=len(saved_run.warnings),
    )
