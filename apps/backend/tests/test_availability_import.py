from datetime import date, time

from app.db.enums import AvailabilityType
from app.services.availability_import import parse_availability_sheet


def test_parse_weekly_availability_sheet_expands_employee_row_to_weekdays() -> None:
    preview = parse_availability_sheet(
        [
            [
                "employee_code",
                "employee_name",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            [
                "E001",
                "John",
                "12:00 - 20:00",
                "N/A",
                "09:00 - 17:00",
                "N/A",
                "10:00 - 18:00",
                "N/A",
            ],
        ],
        week_start=date(2026, 6, 8),
    )

    assert preview.errors == []
    assert len(preview.rows) == 6

    monday = preview.rows[0]
    assert monday.employee_code == "E001"
    assert monday.employee_name == "John"
    assert monday.weekday == "monday"
    assert monday.work_date == date(2026, 6, 8)
    assert monday.start_time == time(12, 0)
    assert monday.end_time == time(20, 0)
    assert monday.availability_type == AvailabilityType.AVAILABLE

    tuesday = preview.rows[1]
    assert tuesday.weekday == "tuesday"
    assert tuesday.work_date == date(2026, 6, 9)
    assert tuesday.start_time is None
    assert tuesday.end_time is None
    assert tuesday.availability_type == AvailabilityType.UNAVAILABLE


def test_parse_weekly_availability_sheet_reports_bad_header() -> None:
    preview = parse_availability_sheet([["wrong", "header"]], week_start=date(2026, 6, 8))

    assert preview.rows == []
    assert preview.errors[0].row_number == 1
    assert preview.errors[0].field == "header"


def test_parse_weekly_availability_sheet_reports_invalid_day_cells() -> None:
    preview = parse_availability_sheet(
        [
            [
                "employee_code",
                "employee_name",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            ["", "John", "bad", "08:00", "18:00 - 09:00", "N/A", "10:00 - 18:00", ""],
        ],
        week_start=date(2026, 6, 8),
    )

    assert preview.rows == []
    assert len(preview.errors) == 1
    assert preview.errors[0].field == "employee_code"


def test_parse_weekly_availability_sheet_reports_bad_day_cells_when_employee_code_exists() -> None:
    preview = parse_availability_sheet(
        [
            [
                "employee_code",
                "employee_name",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            ["E001", "John", "bad", "08:00", "18:00 - 09:00", "N/A", "10:00 - 18:00", ""],
        ],
        week_start=date(2026, 6, 8),
    )

    assert {(error.field, error.row_number) for error in preview.errors} == {
        ("monday", 2),
        ("tuesday", 2),
        ("wednesday", 2),
        ("saturday", 2),
    }
    assert len(preview.rows) == 2
    assert {row.weekday for row in preview.rows} == {"thursday", "friday"}


def test_parse_weekly_availability_sheet_ignores_empty_rows() -> None:
    preview = parse_availability_sheet(
        [
            [
                "employee_code",
                "employee_name",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            ["", "", "", "", "", "", "", ""],
        ],
        week_start=date(2026, 6, 8),
    )

    assert preview.rows == []
    assert preview.errors == []


def test_parse_weekly_availability_sheet_accepts_am_pm_and_off() -> None:
    preview = parse_availability_sheet(
        [
            [
                "employee_code",
                "employee_name",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
            ],
            ["E001", "John", "9AM-5PM", "10 AM - 6 PM", "8:30AM-4:30PM", "Off", "N/A", "off"],
        ],
        week_start=date(2026, 6, 8),
    )

    assert preview.errors == []
    assert len(preview.rows) == 6

    assert preview.rows[0].start_time == time(9, 0)
    assert preview.rows[0].end_time == time(17, 0)
    assert preview.rows[1].start_time == time(10, 0)
    assert preview.rows[1].end_time == time(18, 0)
    assert preview.rows[2].start_time == time(8, 30)
    assert preview.rows[2].end_time == time(16, 30)
    assert preview.rows[3].availability_type == AvailabilityType.UNAVAILABLE
