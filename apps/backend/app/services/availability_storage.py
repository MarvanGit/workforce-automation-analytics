from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AvailabilityRecord, Employee
from app.services.availability_import import AvailabilitySheetPreview


@dataclass(frozen=True)
class AvailabilityImportResult:
    employee_count: int
    availability_count: int


async def save_availability_preview(
    session: AsyncSession,
    preview: AvailabilitySheetPreview,
    week_start: date,
) -> AvailabilityImportResult:
    employee_codes = sorted({row.employee_code for row in preview.rows})

    if not employee_codes:
        return AvailabilityImportResult(employee_count=0, availability_count=0)

    employees = await _load_employees(session, employee_codes)

    for row in preview.rows:
        employee = employees.get(row.employee_code)

        if employee is None:
            employee = Employee(
                employee_code=row.employee_code,
                full_name=row.employee_name or row.employee_code,
            )
            session.add(employee)
            employees[row.employee_code] = employee
        elif row.employee_name:
            employee.full_name = row.employee_name

    await session.flush()
    await _delete_existing_week(session, list(employees.values()), week_start)

    for row in preview.rows:
        employee = employees[row.employee_code]
        session.add(
            AvailabilityRecord(
                employee_id=employee.id,
                work_date=row.work_date,
                start_time=row.start_time,
                end_time=row.end_time,
                availability_type=row.availability_type,
                notes=row.notes,
            )
        )

    try:
        await session.commit()
    except Exception:
        await session.rollback()
        raise

    return AvailabilityImportResult(
        employee_count=len(employee_codes),
        availability_count=len(preview.rows),
    )


async def _load_employees(
    session: AsyncSession,
    employee_codes: list[str],
) -> dict[str, Employee]:
    result = await session.execute(
        select(Employee).where(Employee.employee_code.in_(employee_codes))
    )
    employees = result.scalars().all()
    return {employee.employee_code: employee for employee in employees}


async def _delete_existing_week(
    session: AsyncSession,
    employees: list[Employee],
    week_start: date,
) -> None:
    employee_ids = [employee.id for employee in employees]
    week_end = week_start + timedelta(days=5)

    await session.execute(
        delete(AvailabilityRecord).where(
            AvailabilityRecord.employee_id.in_(employee_ids),
            AvailabilityRecord.work_date >= week_start,
            AvailabilityRecord.work_date <= week_end,
        )
    )
