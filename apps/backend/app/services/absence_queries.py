from dataclasses import dataclass
from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.enums import AbsenceType
from app.db.models import Absence, Employee


@dataclass(frozen=True)
class AbsenceListItem:
    id: str
    employee_id: str
    employee_code: str
    employee_name: str
    start_date: date
    end_date: date
    absence_type: AbsenceType
    notes: str | None


async def list_week_absences(
    session: AsyncSession,
    week_start: date,
) -> list[AbsenceListItem]:
    week_end = week_start + timedelta(days=5)

    result = await session.execute(
        select(Absence, Employee)
        .join(Employee, Absence.employee_id == Employee.id)
        .where(
            Absence.start_date <= week_end,
            Absence.end_date >= week_start,
        )
        .order_by(
            Absence.start_date,
            Employee.employee_code,
        )
    )

    rows = result.all()
    return [_build_absence_item(absence, employee) for absence, employee in rows]


def _build_absence_item(
    absence: Absence,
    employee: Employee,
) -> AbsenceListItem:
    return AbsenceListItem(
        id=absence.id,
        employee_id=employee.id,
        employee_code=employee.employee_code,
        employee_name=employee.full_name,
        start_date=absence.start_date,
        end_date=absence.end_date,
        absence_type=absence.absence_type,
        notes=absence.notes,
    )
