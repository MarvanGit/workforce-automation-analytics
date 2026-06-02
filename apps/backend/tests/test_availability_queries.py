import asyncio
from datetime import date, time

from app.db.enums import AvailabilityType
from app.db.models import AvailabilityRecord, Employee
from app.services.availability_queries import list_employees, list_week_availability


class FakeResult:
    def __init__(self, rows):
        self.rows = rows

    def scalars(self):
        return self

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, rows):
        self.rows = rows

    async def execute(self, statement):
        return FakeResult(self.rows)


def test_list_employees_returns_employee_rows() -> None:
    employee = Employee(employee_code="E001", full_name="Sara Ahmed")
    session = FakeSession(rows=[employee])

    result = asyncio.run(list_employees(session))

    assert result == [employee]


def test_list_week_availability_combines_employee_and_availability_record() -> None:
    employee = Employee(employee_code="E001", full_name="Sara Ahmed")
    employee.id = "employee-1"

    record = AvailabilityRecord(
        employee_id="employee-1",
        work_date=date(2026, 6, 8),
        start_time=time(8, 0),
        end_time=time(16, 0),
        availability_type=AvailabilityType.AVAILABLE,
        notes=None,
    )
    record.id = "availability-1"

    session = FakeSession(rows=[(record, employee)])

    result = asyncio.run(list_week_availability(session, week_start=date(2026, 6, 8)))

    assert len(result) == 1
    assert result[0].id == "availability-1"
    assert result[0].employee_id == "employee-1"
    assert result[0].employee_code == "E001"
    assert result[0].employee_name == "Sara Ahmed"
    assert result[0].availability_type == AvailabilityType.AVAILABLE
