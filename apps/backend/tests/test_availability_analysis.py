from datetime import date, time

from app.db.enums import AvailabilityType
from app.services.availability_analysis import summarize_week_availability
from app.services.availability_queries import AvailabilityListItem


def test_summarize_week_availability_counts_people_and_hours() -> None:
    rows = [
        AvailabilityListItem(
            id="availability-1",
            employee_id="employee-1",
            employee_code="E001",
            employee_name="Sara Ahmed",
            work_date=date(2026, 6, 8),
            start_time=time(9, 0),
            end_time=time(17, 0),
            availability_type=AvailabilityType.AVAILABLE,
            notes=None,
        ),
        AvailabilityListItem(
            id="availability-2",
            employee_id="employee-2",
            employee_code="E002",
            employee_name="John Doe",
            work_date=date(2026, 6, 8),
            start_time=None,
            end_time=None,
            availability_type=AvailabilityType.UNAVAILABLE,
            notes=None,
        ),
        AvailabilityListItem(
            id="availability-3",
            employee_id="employee-1",
            employee_code="E001",
            employee_name="Sara Ahmed",
            work_date=date(2026, 6, 9),
            start_time=time(10, 0),
            end_time=time(14, 0),
            availability_type=AvailabilityType.AVAILABLE,
            notes=None,
        ),
        AvailabilityListItem(
            id="availability-4",
            employee_id="employee-2",
            employee_code="E002",
            employee_name="John Doe",
            work_date=date(2026, 6, 9),
            start_time=time(12, 0),
            end_time=time(18, 0),
            availability_type=AvailabilityType.AVAILABLE,
            notes=None,
        ),
    ]

    summary = summarize_week_availability(rows, week_start=date(2026, 6, 8))

    monday = summary.days[0]
    tuesday = summary.days[1]

    assert summary.week_end == date(2026, 6, 13)
    assert len(summary.days) == 6
    assert monday.weekday == "monday"
    assert monday.available_employee_count == 1
    assert monday.unavailable_employee_count == 1
    assert monday.available_hours == 8
    assert tuesday.available_employee_count == 2
    assert tuesday.unavailable_employee_count == 0
    assert tuesday.available_hours == 10

    assert len(summary.employees) == 2
    assert summary.employees[0].employee_code == "E001"
    assert summary.employees[0].available_hours == 12
    assert summary.employees[1].employee_code == "E002"
    assert summary.employees[1].available_hours == 6


def test_summarize_week_availability_returns_empty_days() -> None:
    summary = summarize_week_availability([], week_start=date(2026, 6, 8))

    assert len(summary.days) == 6
    assert summary.days[0].work_date == date(2026, 6, 8)
    assert summary.days[5].work_date == date(2026, 6, 13)
    assert summary.days[0].available_employee_count == 0
    assert summary.days[0].unavailable_employee_count == 0
    assert summary.days[0].available_hours == 0
    assert summary.employees == []
