from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from app.db.enums import AvailabilityType

EXPECTED_HEADERS = [
    "employee_code",
    "employee_name",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]

WEEKDAYS = [
    ("monday", 0),
    ("tuesday", 1),
    ("wednesday", 2),
    ("thursday", 3),
    ("friday", 4),
    ("saturday", 5),
]

NOT_AVAILABLE_VALUES = {"n/a", "na", "not available", "unavailable", "off"}


@dataclass(frozen=True)
class AvailabilitySheetRow:
    row_number: int
    employee_code: str
    employee_name: str | None
    weekday: str
    work_date: date
    start_time: time | None
    end_time: time | None
    availability_type: AvailabilityType
    notes: str | None


@dataclass(frozen=True)
class AvailabilitySheetError:
    row_number: int
    field: str
    message: str


@dataclass(frozen=True)
class AvailabilitySheetPreview:
    rows: list[AvailabilitySheetRow]
    errors: list[AvailabilitySheetError]


def parse_availability_sheet(values: list[list[str]], week_start: date) -> AvailabilitySheetPreview:
    if not values:
        return AvailabilitySheetPreview(
            rows=[],
            errors=[
                AvailabilitySheetError(
                    row_number=1,
                    field="header",
                    message="Sheet is empty.",
                )
            ],
        )

    headers = [_clean_header(cell) for cell in values[0]]
    if headers[: len(EXPECTED_HEADERS)] != EXPECTED_HEADERS:
        return AvailabilitySheetPreview(
            rows=[],
            errors=[
                AvailabilitySheetError(
                    row_number=1,
                    field="header",
                    message=f"Expected headers: {', '.join(EXPECTED_HEADERS)}.",
                )
            ],
        )

    parsed_rows: list[AvailabilitySheetRow] = []
    errors: list[AvailabilitySheetError] = []

    for row_number, row in enumerate(values[1:], start=2):
        if _is_empty_row(row):
            continue

        normalized_row = _pad_row(row)
        employee_code = normalized_row[0].strip()
        employee_name = _optional_text(normalized_row[1])

        if not employee_code:
            errors.append(_error(row_number, "employee_code", "Employee code is required."))
            continue

        for weekday, day_offset in WEEKDAYS:
            cell = normalized_row[day_offset + 2]
            parsed_cell = _parse_day_cell(cell)

            if parsed_cell is None:
                errors.append(
                    _error(
                        row_number,
                        weekday,
                        "Use HH:MM - HH:MM or N/A.",
                    )
                )
                continue

            start_time, end_time, availability_type = parsed_cell
            parsed_rows.append(
                AvailabilitySheetRow(
                    row_number=row_number,
                    employee_code=employee_code,
                    employee_name=employee_name,
                    weekday=weekday,
                    work_date=week_start + timedelta(days=day_offset),
                    start_time=start_time,
                    end_time=end_time,
                    availability_type=availability_type,
                    notes=None,
                )
            )

    return AvailabilitySheetPreview(rows=parsed_rows, errors=errors)


def _parse_day_cell(value: str) -> tuple[time | None, time | None, AvailabilityType] | None:
    cleaned = value.strip().lower()

    if cleaned in NOT_AVAILABLE_VALUES:
        return None, None, AvailabilityType.UNAVAILABLE

    if not cleaned:
        return None

    parts = [part.strip() for part in cleaned.split("-")]
    if len(parts) != 2:
        return None

    start_time = _parse_time(parts[0])
    end_time = _parse_time(parts[1])

    if start_time is None or end_time is None:
        return None
    if start_time >= end_time:
        return None

    return start_time, end_time, AvailabilityType.AVAILABLE


def _clean_header(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def _pad_row(row: list[str]) -> list[str]:
    return (row + [""] * len(EXPECTED_HEADERS))[: len(EXPECTED_HEADERS)]


def _is_empty_row(row: list[str]) -> bool:
    return not any(cell.strip() for cell in row)


def _optional_text(value: str) -> str | None:
    cleaned = value.strip()
    return cleaned or None


def _parse_time(value: str) -> time | None:
    cleaned = value.strip().upper()

    try:
        return time.fromisoformat(cleaned)
    except ValueError:
        pass

    for time_format in ["%I%p", "%I %p", "%I:%M%p", "%I:%M %p"]:
        try:
            return datetime.strptime(cleaned, time_format).time()
        except ValueError:
            continue

    return None


def _error(row_number: int, field: str, message: str) -> AvailabilitySheetError:
    return AvailabilitySheetError(row_number=row_number, field=field, message=message)
