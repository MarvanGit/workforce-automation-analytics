from datetime import date, time

from app.db.enums import AbsenceType, AvailabilityType
from app.services.absence_queries import AbsenceListItem
from app.services.availability_queries import AvailabilityListItem
from app.services.scheduling_preview import build_schedule_preview
from app.services.shift_queries import ShiftDemandListItem


def test_build_schedule_preview_assigns_available_employees() -> None:
    availability_rows = [
        _availability("employee-1", "E001", "Sara Ahmed", time(9, 0), time(17, 0)),
        _availability("employee-2", "E002", "John Doe", time(9, 0), time(17, 0)),
    ]
    demand_rows = [_demand(required_employee_count=2)]

    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=availability_rows,
        absence_rows=[],
        demand_rows=demand_rows,
    )

    shift = preview.shifts[0]

    assert preview.week_end == date(2026, 6, 13)
    assert shift.weekday == "monday"
    assert shift.missing_employee_count == 0
    assert [employee.employee_code for employee in shift.assigned_employees] == [
        "E001",
        "E002",
    ]
    assert preview.warnings == []


def test_build_schedule_preview_skips_absent_employees() -> None:
    availability_rows = [
        _availability("employee-1", "E001", "Sara Ahmed", time(9, 0), time(17, 0)),
        _availability("employee-2", "E002", "John Doe", time(9, 0), time(17, 0)),
    ]
    absence_rows = [
        AbsenceListItem(
            id="absence-1",
            employee_id="employee-1",
            employee_code="E001",
            employee_name="Sara Ahmed",
            start_date=date(2026, 6, 8),
            end_date=date(2026, 6, 8),
            absence_type=AbsenceType.VACATION,
            notes=None,
        )
    ]
    demand_rows = [_demand(required_employee_count=2)]

    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=availability_rows,
        absence_rows=absence_rows,
        demand_rows=demand_rows,
    )

    shift = preview.shifts[0]

    assert [employee.employee_code for employee in shift.assigned_employees] == ["E002"]
    assert shift.missing_employee_count == 1
    assert preview.warnings == ["2026-06-08 Morning needs 1 more employee(s)."]


def test_build_schedule_preview_requires_full_shift_availability() -> None:
    availability_rows = [
        _availability("employee-1", "E001", "Sara Ahmed", time(10, 0), time(17, 0)),
    ]
    demand_rows = [_demand(required_employee_count=1)]

    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=availability_rows,
        absence_rows=[],
        demand_rows=demand_rows,
    )

    shift = preview.shifts[0]

    assert shift.assigned_employees == []
    assert shift.missing_employee_count == 1


def test_build_schedule_preview_does_not_double_assign_same_day() -> None:
    availability_rows = [
        _availability("employee-1", "E001", "Sara Ahmed", time(9, 0), time(20, 0)),
    ]
    demand_rows = [
        _demand(
            demand_id="demand-1",
            shift_template_name="Morning",
            shift_start_time=time(9, 0),
            shift_end_time=time(17, 0),
        ),
        _demand(
            demand_id="demand-2",
            shift_template_name="Evening",
            shift_start_time=time(17, 0),
            shift_end_time=time(20, 0),
        ),
    ]

    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=availability_rows,
        absence_rows=[],
        demand_rows=demand_rows,
    )

    assert len(preview.shifts[0].assigned_employees) == 1
    assert preview.shifts[1].assigned_employees == []
    assert preview.shifts[1].missing_employee_count == 1


def test_build_schedule_preview_spreads_assignments_across_week() -> None:
    availability_rows = [
        _availability("employee-1", "E001", "Sara Ahmed", time(9, 0), time(17, 0)),
        _availability("employee-2", "E002", "John Doe", time(9, 0), time(17, 0)),
        _availability(
            "employee-1",
            "E001",
            "Sara Ahmed",
            time(9, 0),
            time(17, 0),
            work_date=date(2026, 6, 9),
        ),
        _availability(
            "employee-2",
            "E002",
            "John Doe",
            time(9, 0),
            time(17, 0),
            work_date=date(2026, 6, 9),
        ),
    ]
    demand_rows = [
        _demand(demand_id="demand-1", demand_date=date(2026, 6, 8)),
        _demand(demand_id="demand-2", demand_date=date(2026, 6, 9)),
    ]

    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=availability_rows,
        absence_rows=[],
        demand_rows=demand_rows,
    )

    assert preview.shifts[0].assigned_employees[0].employee_code == "E001"
    assert preview.shifts[1].assigned_employees[0].employee_code == "E002"


def test_build_schedule_preview_warns_when_no_demand_exists() -> None:
    preview = build_schedule_preview(
        week_start=date(2026, 6, 8),
        availability_rows=[],
        absence_rows=[],
        demand_rows=[],
    )

    assert preview.shifts == []
    assert preview.warnings == ["No shift demand found for this week."]


def _availability(
    employee_id: str,
    employee_code: str,
    employee_name: str,
    start_time: time,
    end_time: time,
    work_date: date = date(2026, 6, 8),
) -> AvailabilityListItem:
    return AvailabilityListItem(
        id=f"availability-{employee_id}",
        employee_id=employee_id,
        employee_code=employee_code,
        employee_name=employee_name,
        work_date=work_date,
        start_time=start_time,
        end_time=end_time,
        availability_type=AvailabilityType.AVAILABLE,
        notes=None,
    )


def _demand(
    demand_id: str = "demand-1",
    demand_date: date = date(2026, 6, 8),
    shift_template_name: str = "Morning",
    shift_start_time: time = time(9, 0),
    shift_end_time: time = time(17, 0),
    required_employee_count: int = 1,
) -> ShiftDemandListItem:
    return ShiftDemandListItem(
        id=demand_id,
        demand_date=demand_date,
        shift_template_id="template-1",
        shift_template_name=shift_template_name,
        shift_start_time=shift_start_time,
        shift_end_time=shift_end_time,
        required_employee_count=required_employee_count,
        notes=None,
    )
