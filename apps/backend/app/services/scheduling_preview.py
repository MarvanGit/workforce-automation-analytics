from dataclasses import dataclass
from datetime import date, time, timedelta

from app.db.enums import AvailabilityType
from app.services.absence_queries import AbsenceListItem
from app.services.availability_queries import AvailabilityListItem
from app.services.shift_queries import ShiftDemandListItem

WEEKDAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]


@dataclass(frozen=True)
class ScheduleEmployeePreview:
    employee_id: str
    employee_code: str
    employee_name: str


@dataclass(frozen=True)
class ScheduleShiftPreview:
    demand_id: str
    demand_date: date
    weekday: str
    shift_template_id: str
    shift_template_name: str
    shift_start_time: time
    shift_end_time: time
    required_employee_count: int
    assigned_employees: list[ScheduleEmployeePreview]
    missing_employee_count: int


@dataclass(frozen=True)
class SchedulePreview:
    week_start: date
    week_end: date
    shifts: list[ScheduleShiftPreview]
    warnings: list[str]


def build_schedule_preview(
    week_start: date,
    availability_rows: list[AvailabilityListItem],
    absence_rows: list[AbsenceListItem],
    demand_rows: list[ShiftDemandListItem],
) -> SchedulePreview:
    assigned_employee_ids_by_date: dict[date, set[str]] = {}
    assignment_counts_by_employee_id: dict[str, int] = {}
    shift_previews = []
    warnings = []

    for demand in demand_rows:
        assigned_employees = _choose_employees(
            demand=demand,
            availability_rows=availability_rows,
            absence_rows=absence_rows,
            already_assigned_ids=assigned_employee_ids_by_date.setdefault(
                demand.demand_date,
                set(),
            ),
            assignment_counts_by_employee_id=assignment_counts_by_employee_id,
        )

        missing_count = demand.required_employee_count - len(assigned_employees)
        if missing_count > 0:
            warnings.append(
                _missing_staff_warning(demand, missing_count)
            )

        shift_previews.append(
            ScheduleShiftPreview(
                demand_id=demand.id,
                demand_date=demand.demand_date,
                weekday=WEEKDAY_NAMES[demand.demand_date.weekday()],
                shift_template_id=demand.shift_template_id,
                shift_template_name=demand.shift_template_name,
                shift_start_time=demand.shift_start_time,
                shift_end_time=demand.shift_end_time,
                required_employee_count=demand.required_employee_count,
                assigned_employees=assigned_employees,
                missing_employee_count=missing_count,
            )
        )

    if len(demand_rows) == 0:
        warnings.append("No shift demand found for this week.")

    return SchedulePreview(
        week_start=week_start,
        week_end=week_start + timedelta(days=5),
        shifts=shift_previews,
        warnings=warnings,
    )


def _choose_employees(
    demand: ShiftDemandListItem,
    availability_rows: list[AvailabilityListItem],
    absence_rows: list[AbsenceListItem],
    already_assigned_ids: set[str],
    assignment_counts_by_employee_id: dict[str, int],
) -> list[ScheduleEmployeePreview]:
    candidates = []

    for availability in availability_rows:
        if not _can_work_shift(demand, availability, absence_rows, already_assigned_ids):
            continue

        candidates.append(
            ScheduleEmployeePreview(
                employee_id=availability.employee_id,
                employee_code=availability.employee_code,
                employee_name=availability.employee_name,
            )
        )

    candidates.sort(
        key=lambda employee: (
            assignment_counts_by_employee_id.get(employee.employee_id, 0),
            employee.employee_code,
        )
    )
    selected_employees = candidates[: demand.required_employee_count]

    for employee in selected_employees:
        already_assigned_ids.add(employee.employee_id)
        current_count = assignment_counts_by_employee_id.get(employee.employee_id, 0)
        assignment_counts_by_employee_id[employee.employee_id] = current_count + 1

    return selected_employees


def _can_work_shift(
    demand: ShiftDemandListItem,
    availability: AvailabilityListItem,
    absence_rows: list[AbsenceListItem],
    already_assigned_ids: set[str],
) -> bool:
    if availability.work_date != demand.demand_date:
        return False

    if availability.availability_type != AvailabilityType.AVAILABLE:
        return False

    if availability.employee_id in already_assigned_ids:
        return False

    if _is_absent(availability.employee_id, demand.demand_date, absence_rows):
        return False

    return _availability_covers_shift(
        availability.start_time,
        availability.end_time,
        demand.shift_start_time,
        demand.shift_end_time,
    )


def _is_absent(
    employee_id: str,
    work_date: date,
    absence_rows: list[AbsenceListItem],
) -> bool:
    for absence in absence_rows:
        if absence.employee_id != employee_id:
            continue

        if absence.start_date <= work_date <= absence.end_date:
            return True

    return False


def _availability_covers_shift(
    availability_start: time | None,
    availability_end: time | None,
    shift_start: time,
    shift_end: time,
) -> bool:
    if availability_start is None or availability_end is None:
        return False

    return availability_start <= shift_start and availability_end >= shift_end


def _missing_staff_warning(
    demand: ShiftDemandListItem,
    missing_count: int,
) -> str:
    return (
        f"{demand.demand_date} {demand.shift_template_name} needs "
        f"{missing_count} more employee(s)."
    )
