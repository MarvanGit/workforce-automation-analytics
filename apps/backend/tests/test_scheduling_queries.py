import asyncio
from datetime import UTC, date, datetime

from app.db.enums import SchedulingRunStatus
from app.db.models import Employee, ScheduledShift, SchedulingRun, ShiftTemplate
from app.services.scheduling_queries import get_schedule_run, list_schedule_runs


class FakeScalarResult:
    def __init__(self, rows):
        self.rows = rows

    def scalars(self):
        return self

    def all(self):
        return self.rows


class FakeRowResult:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeSession:
    def __init__(self, run=None, run_rows=None, shift_rows=None) -> None:
        self.run = run
        self.run_rows = run_rows or []
        self.shift_rows = shift_rows or []

    async def get(self, model, item_id):
        return self.run

    async def execute(self, statement):
        if statement.__visit_name__ == "select" and self.shift_rows:
            return FakeRowResult(self.shift_rows)

        return FakeScalarResult(self.run_rows)


def test_list_schedule_runs_returns_saved_runs() -> None:
    run = SchedulingRun(
        start_date=date(2026, 6, 8),
        end_date=date(2026, 6, 13),
        status=SchedulingRunStatus.COMPLETED,
    )
    run.id = "run-1"
    session = FakeSession(run_rows=[run])

    result = asyncio.run(list_schedule_runs(session))

    assert len(result) == 1
    assert result[0].id == "run-1"
    assert result[0].status == SchedulingRunStatus.COMPLETED


def test_get_schedule_run_returns_run_with_scheduled_shifts() -> None:
    run = SchedulingRun(
        start_date=date(2026, 6, 8),
        end_date=date(2026, 6, 13),
        status=SchedulingRunStatus.COMPLETED,
    )
    run.id = "run-1"

    shift = ScheduledShift(
        scheduling_run_id="run-1",
        employee_id="employee-1",
        shift_template_id="template-1",
        shift_date=date(2026, 6, 8),
        start_datetime=datetime(2026, 6, 8, 9, 0, tzinfo=UTC),
        end_datetime=datetime(2026, 6, 8, 17, 0, tzinfo=UTC),
    )
    shift.id = "scheduled-shift-1"

    employee = Employee(employee_code="E001", full_name="Sara Ahmed")
    employee.id = "employee-1"

    template = ShiftTemplate(
        name="Morning",
        start_time=datetime(2026, 6, 8, 9, 0).time(),
        end_time=datetime(2026, 6, 8, 17, 0).time(),
        duration_minutes=480,
        is_overnight=False,
        active=True,
    )
    template.id = "template-1"

    session = FakeSession(
        run=run,
        shift_rows=[(shift, employee, template)],
    )

    result = asyncio.run(get_schedule_run(session, "run-1"))

    assert result is not None
    assert result.id == "run-1"
    assert result.scheduled_shifts[0].id == "scheduled-shift-1"
    assert result.scheduled_shifts[0].employee_code == "E001"
    assert result.scheduled_shifts[0].shift_template_name == "Morning"


def test_get_schedule_run_returns_none_when_missing() -> None:
    session = FakeSession(run=None)

    result = asyncio.run(get_schedule_run(session, "missing-run"))

    assert result is None
