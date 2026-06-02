import asyncio
from datetime import date, time

from app.db.enums import AvailabilityType
from app.db.models import AvailabilityRecord, Employee
from app.services.availability_import import AvailabilitySheetPreview, AvailabilitySheetRow
from app.services.availability_storage import save_availability_preview


class FakeResult:
    def __init__(self, employees: list[Employee]) -> None:
        self.employees = employees

    def scalars(self) -> "FakeResult":
        return self

    def all(self) -> list[Employee]:
        return self.employees


class FakeSession:
    def __init__(self, employees: list[Employee] | None = None) -> None:
        self.employees = employees or []
        self.added: list[object] = []
        self.committed = False
        self.rolled_back = False
        self.deleted_existing_week = False

    async def execute(self, statement):
        if statement.__visit_name__ == "select":
            return FakeResult(self.employees)

        if statement.__visit_name__ == "delete":
            self.deleted_existing_week = True
            return None

        raise AssertionError(f"Unexpected statement: {statement}")

    def add(self, item: object) -> None:
        self.added.append(item)

    async def flush(self) -> None:
        for item in self.added:
            if isinstance(item, Employee) and item.id is None:
                item.id = f"id-{item.employee_code}"

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def test_save_availability_preview_creates_employee_and_records() -> None:
    session = FakeSession()
    preview = AvailabilitySheetPreview(
        rows=[
            AvailabilitySheetRow(
                row_number=2,
                employee_code="E001",
                employee_name="Sara Ahmed",
                weekday="monday",
                work_date=date(2026, 6, 8),
                start_time=time(8, 0),
                end_time=time(16, 0),
                availability_type=AvailabilityType.AVAILABLE,
                notes=None,
            ),
            AvailabilitySheetRow(
                row_number=2,
                employee_code="E001",
                employee_name="Sara Ahmed",
                weekday="tuesday",
                work_date=date(2026, 6, 9),
                start_time=None,
                end_time=None,
                availability_type=AvailabilityType.UNAVAILABLE,
                notes=None,
            ),
        ],
        errors=[],
    )

    result = asyncio.run(
        save_availability_preview(session, preview, week_start=date(2026, 6, 8))
    )

    employees = [item for item in session.added if isinstance(item, Employee)]
    availability_records = [
        item for item in session.added if isinstance(item, AvailabilityRecord)
    ]

    assert result.employee_count == 1
    assert result.availability_count == 2
    assert employees[0].employee_code == "E001"
    assert employees[0].full_name == "Sara Ahmed"
    assert len(availability_records) == 2
    assert availability_records[0].employee_id == "id-E001"
    assert session.deleted_existing_week is True
    assert session.committed is True
    assert session.rolled_back is False


def test_save_availability_preview_updates_existing_employee_name() -> None:
    employee = Employee(employee_code="E001", full_name="Old Name")
    employee.id = "employee-1"
    session = FakeSession(employees=[employee])
    preview = AvailabilitySheetPreview(
        rows=[
            AvailabilitySheetRow(
                row_number=2,
                employee_code="E001",
                employee_name="New Name",
                weekday="monday",
                work_date=date(2026, 6, 8),
                start_time=time(8, 0),
                end_time=time(16, 0),
                availability_type=AvailabilityType.AVAILABLE,
                notes=None,
            )
        ],
        errors=[],
    )

    result = asyncio.run(
        save_availability_preview(session, preview, week_start=date(2026, 6, 8))
    )

    employees_added = [item for item in session.added if isinstance(item, Employee)]
    availability_records = [
        item for item in session.added if isinstance(item, AvailabilityRecord)
    ]

    assert result.employee_count == 1
    assert result.availability_count == 1
    assert employees_added == []
    assert employee.full_name == "New Name"
    assert availability_records[0].employee_id == "employee-1"
