from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import SchedulingRunStatus
from app.db.models import Employee, ScheduledShift, SchedulingRun, ShiftTemplate
from app.services.scheduling_storage import SavedScheduledShift, SavedScheduleRun


@dataclass(frozen=True)
class ScheduleRunListItem:
    id: str
    start_date: date
    end_date: date
    status: SchedulingRunStatus


async def list_schedule_runs(session: AsyncSession) -> list[ScheduleRunListItem]:
    result = await session.execute(
        select(SchedulingRun).order_by(
            SchedulingRun.start_date.desc(),
            SchedulingRun.created_at.desc(),
        )
    )
    runs = result.scalars().all()
    return [_build_schedule_run_list_item(run) for run in runs]


async def get_schedule_run(
    session: AsyncSession,
    run_id: str,
) -> SavedScheduleRun | None:
    run = await session.get(SchedulingRun, run_id)
    if run is None:
        return None

    result = await session.execute(
        select(ScheduledShift, Employee, ShiftTemplate)
        .join(Employee, ScheduledShift.employee_id == Employee.id)
        .join(ShiftTemplate, ScheduledShift.shift_template_id == ShiftTemplate.id)
        .where(ScheduledShift.scheduling_run_id == run_id)
        .order_by(
            ScheduledShift.shift_date,
            ShiftTemplate.start_time,
            Employee.employee_code,
        )
    )

    rows = result.all()
    scheduled_shifts = [
        _build_saved_scheduled_shift(shift, employee, template)
        for shift, employee, template in rows
    ]

    return SavedScheduleRun(
        id=run.id,
        start_date=run.start_date,
        end_date=run.end_date,
        status=run.status,
        scheduled_shifts=scheduled_shifts,
        warnings=[],
    )


def _build_schedule_run_list_item(
    run: SchedulingRun,
) -> ScheduleRunListItem:
    return ScheduleRunListItem(
        id=run.id,
        start_date=run.start_date,
        end_date=run.end_date,
        status=run.status,
    )


def _build_saved_scheduled_shift(
    shift: ScheduledShift,
    employee: Employee,
    template: ShiftTemplate,
) -> SavedScheduledShift:
    return SavedScheduledShift(
        id=shift.id,
        employee_id=employee.id,
        employee_code=employee.employee_code,
        employee_name=employee.full_name,
        shift_date=shift.shift_date,
        shift_template_id=template.id,
        shift_template_name=template.name,
        start_datetime=shift.start_datetime,
        end_datetime=shift.end_datetime,
    )
