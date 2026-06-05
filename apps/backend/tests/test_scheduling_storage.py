import asyncio
from datetime import UTC, date, datetime, time

from app.db.enums import SchedulingRunStatus
from app.db.models import ScheduledShift, SchedulingRun
from app.services.scheduling_preview import (
    ScheduleEmployeePreview,
    SchedulePreview,
    ScheduleShiftPreview,
)
from app.services.scheduling_storage import save_schedule_preview


class FakeSession:
    def __init__(self) -> None:
        self.added: list[object] = []
        self.committed = False
        self.rolled_back = False

    def add(self, item: object) -> None:
        self.added.append(item)

    async def flush(self) -> None:
        run_count = 1
        shift_count = 1

        for item in self.added:
            if isinstance(item, SchedulingRun) and item.id is None:
                item.id = f"run-{run_count}"
                run_count += 1

            if isinstance(item, ScheduledShift) and item.id is None:
                item.id = f"scheduled-shift-{shift_count}"
                shift_count += 1

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


def test_save_schedule_preview_creates_run_and_scheduled_shift() -> None:
    session = FakeSession()
    preview = SchedulePreview(
        week_start=date(2026, 6, 8),
        week_end=date(2026, 6, 13),
        shifts=[
            ScheduleShiftPreview(
                demand_id="demand-1",
                demand_date=date(2026, 6, 8),
                weekday="monday",
                shift_template_id="template-1",
                shift_template_name="Morning",
                shift_start_time=time(9, 0),
                shift_end_time=time(17, 0),
                required_employee_count=1,
                assigned_employees=[
                    ScheduleEmployeePreview(
                        employee_id="employee-1",
                        employee_code="E001",
                        employee_name="Sara Ahmed",
                    )
                ],
                missing_employee_count=0,
            )
        ],
        warnings=[],
    )

    result = asyncio.run(save_schedule_preview(session, preview))

    runs = [item for item in session.added if isinstance(item, SchedulingRun)]
    scheduled_shifts = [
        item for item in session.added if isinstance(item, ScheduledShift)
    ]

    assert result.id == "run-1"
    assert result.status == SchedulingRunStatus.COMPLETED
    assert result.scheduled_shifts[0].id == "scheduled-shift-1"
    assert result.scheduled_shifts[0].employee_code == "E001"
    assert result.scheduled_shifts[0].start_datetime == datetime(
        2026,
        6,
        8,
        9,
        0,
        tzinfo=UTC,
    )
    assert result.scheduled_shifts[0].end_datetime == datetime(
        2026,
        6,
        8,
        17,
        0,
        tzinfo=UTC,
    )
    assert len(runs) == 1
    assert len(scheduled_shifts) == 1
    assert scheduled_shifts[0].scheduling_run_id == "run-1"
    assert session.committed is True
    assert session.rolled_back is False
