from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import SchedulingRunStatus
from app.db.models import ScheduledShift, SchedulingRun
from app.services.scheduling_preview import SchedulePreview


@dataclass(frozen=True)
class SavedScheduledShift:
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    shift_date: date
    shift_template_id: str
    shift_template_name: str
    start_datetime: datetime
    end_datetime: datetime


@dataclass(frozen=True)
class SavedScheduleRun:
    id: str
    start_date: date
    end_date: date
    status: SchedulingRunStatus
    scheduled_shifts: list[SavedScheduledShift]
    warnings: list[str]


async def save_schedule_preview(
    session: AsyncSession,
    preview: SchedulePreview,
) -> SavedScheduleRun:
    run = SchedulingRun(
        start_date=preview.week_start,
        end_date=preview.week_end,
        status=SchedulingRunStatus.COMPLETED,
    )
    session.add(run)
    await session.flush()

    saved_shifts = []

    for shift in preview.shifts:
        for employee in shift.assigned_employees:
            scheduled_shift = ScheduledShift(
                scheduling_run_id=run.id,
                employee_id=employee.employee_id,
                shift_template_id=shift.shift_template_id,
                shift_date=shift.demand_date,
                start_datetime=_shift_datetime(shift.demand_date, shift.shift_start_time),
                end_datetime=_shift_end_datetime(
                    shift.demand_date,
                    shift.shift_start_time,
                    shift.shift_end_time,
                ),
            )
            session.add(scheduled_shift)
            saved_shifts.append((scheduled_shift, shift, employee))

    try:
        await session.flush()
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return SavedScheduleRun(
        id=run.id,
        start_date=run.start_date,
        end_date=run.end_date,
        status=run.status,
        scheduled_shifts=[
            SavedScheduledShift(
                id=scheduled_shift.id,
                employee_id=employee.employee_id,
                employee_code=employee.employee_code,
                employee_name=employee.employee_name,
                shift_date=scheduled_shift.shift_date,
                shift_template_id=shift.shift_template_id,
                shift_template_name=shift.shift_template_name,
                start_datetime=scheduled_shift.start_datetime,
                end_datetime=scheduled_shift.end_datetime,
            )
            for scheduled_shift, shift, employee in saved_shifts
        ],
        warnings=preview.warnings,
    )


def _shift_datetime(shift_date: date, shift_time: time) -> datetime:
    return datetime.combine(shift_date, shift_time, tzinfo=UTC)


def _shift_end_datetime(
    shift_date: date,
    shift_start_time: time,
    shift_end_time: time,
) -> datetime:
    end_date = shift_date

    if shift_end_time < shift_start_time:
        end_date = shift_date + timedelta(days=1)

    return _shift_datetime(end_date, shift_end_time)
