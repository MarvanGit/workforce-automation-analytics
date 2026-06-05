from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.db.enums import AvailabilityType
from app.services.availability_queries import AvailabilityListItem

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]


@dataclass(frozen=True)
class DayAvailabilitySummary:
    weekday: str
    work_date: date
    available_employee_count: int
    unavailable_employee_count: int
    available_hours: float


@dataclass(frozen=True)
class EmployeeAvailabilitySummary:
    employee_id: str
    employee_code: str
    employee_name: str
    available_hours: float


@dataclass(frozen=True)
class AvailabilitySummary:
    week_start: date
    week_end: date
    days: list[DayAvailabilitySummary]
    employees: list[EmployeeAvailabilitySummary]


def summarize_week_availability(
    rows: list[AvailabilityListItem],
    week_start: date,
) -> AvailabilitySummary:
    week_days = _week_days(week_start)

    available_employee_ids = {work_date: set() for _, work_date in week_days}
    unavailable_employee_ids = {work_date: set() for _, work_date in week_days}
    available_hours_by_day = {work_date: 0.0 for _, work_date in week_days}

    employee_names: dict[str, tuple[str, str]] = {}
    available_hours_by_employee: dict[str, float] = {}

    for row in rows:
        if row.work_date not in available_hours_by_day:
            continue

        employee_names[row.employee_id] = (row.employee_code, row.employee_name)
        available_hours_by_employee.setdefault(row.employee_id, 0.0)

        if row.availability_type == AvailabilityType.UNAVAILABLE:
            unavailable_employee_ids[row.work_date].add(row.employee_id)
            continue

        available_employee_ids[row.work_date].add(row.employee_id)
        hours = _available_hours(row.start_time, row.end_time)
        available_hours_by_day[row.work_date] += hours
        available_hours_by_employee[row.employee_id] += hours

    day_summaries = [
        DayAvailabilitySummary(
            weekday=weekday,
            work_date=work_date,
            available_employee_count=len(available_employee_ids[work_date]),
            unavailable_employee_count=len(unavailable_employee_ids[work_date]),
            available_hours=available_hours_by_day[work_date],
        )
        for weekday, work_date in week_days
    ]

    employee_summaries = [
        EmployeeAvailabilitySummary(
            employee_id=employee_id,
            employee_code=employee_code,
            employee_name=employee_name,
            available_hours=available_hours_by_employee[employee_id],
        )
        for employee_id, (employee_code, employee_name) in sorted(
            employee_names.items(),
            key=lambda item: item[1][0],
        )
    ]

    return AvailabilitySummary(
        week_start=week_start,
        week_end=week_start + timedelta(days=5),
        days=day_summaries,
        employees=employee_summaries,
    )


def _week_days(week_start: date) -> list[tuple[str, date]]:
    return [
        (weekday, week_start + timedelta(days=day_number))
        for day_number, weekday in enumerate(WEEKDAY_NAMES)
    ]


def _available_hours(start_time: time | None, end_time: time | None) -> float:
    if start_time is None or end_time is None:
        return 0.0

    start_datetime = datetime.combine(date.today(), start_time)
    end_datetime = datetime.combine(date.today(), end_time)
    return (end_datetime - start_datetime).total_seconds() / 3600
