from dataclasses import dataclass
from datetime import date, time, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import AvailabilityType
from app.db.models import AvailabilityRecord, Employee


@dataclass(frozen=True)
class AvailabilityListItem:
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    work_date: date
    start_time: time | None
    end_time: time | None
    availability_type: AvailabilityType
    notes: str | None


async def list_employees(session: AsyncSession) -> list[Employee]:
    result = await session.execute(select(Employee).order_by(Employee.employee_code))
    return list(result.scalars().all())


async def list_week_availability(
    session: AsyncSession,
    week_start: date,
) -> list[AvailabilityListItem]:
    week_end = week_start + timedelta(days=5)

    result = await session.execute(
        select(AvailabilityRecord, Employee)
        .join(Employee, AvailabilityRecord.employee_id == Employee.id)
        .where(
            AvailabilityRecord.work_date >= week_start,
            AvailabilityRecord.work_date <= week_end,
        )
        .order_by(
            Employee.employee_code,
            AvailabilityRecord.work_date,
            AvailabilityRecord.start_time,
        )
    )

    rows = result.all()
    return [_build_availability_item(record, employee) for record, employee in rows]


def _build_availability_item(
    record: AvailabilityRecord,
    employee: Employee,
) -> AvailabilityListItem:
    return AvailabilityListItem(
        id=record.id,
        employee_id=employee.id,
        employee_code=employee.employee_code,
        employee_name=employee.full_name,
        work_date=record.work_date,
        start_time=record.start_time,
        end_time=record.end_time,
        availability_type=record.availability_type,
        notes=record.notes,
    )
