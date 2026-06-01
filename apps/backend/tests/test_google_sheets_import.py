import pytest
from fastapi.testclient import TestClient

from app.integrations.google_sheets import GoogleSheetsConfigError, read_sheet_values
from app.main import app


class FakeRequest:
    def execute(self) -> dict[str, list[list[str]]]:
        return {"values": [["employee_code"], ["E001"]]}


class FakeValues:
    def __init__(self) -> None:
        self.spreadsheet_id = ""
        self.sheet_range = ""

    def get(self, spreadsheetId: str, range: str) -> FakeRequest:
        self.spreadsheet_id = spreadsheetId
        self.sheet_range = range
        return FakeRequest()


class FakeSpreadsheets:
    def __init__(self, values: FakeValues) -> None:
        self._values = values

    def values(self) -> FakeValues:
        return self._values


class FakeService:
    def __init__(self, values: FakeValues) -> None:
        self._values = values

    def spreadsheets(self) -> FakeSpreadsheets:
        return FakeSpreadsheets(self._values)


def test_read_sheet_values_calls_google_values_get() -> None:
    values = FakeValues()
    service = FakeService(values)

    result = read_sheet_values(
        spreadsheet_id="spreadsheet-123",
        sheet_range="Availability!A:H",
        credentials_path="unused-in-test.json",
        service=service,
    )

    assert result == [["employee_code"], ["E001"]]
    assert values.spreadsheet_id == "spreadsheet-123"
    assert values.sheet_range == "Availability!A:H"


def test_read_sheet_values_requires_spreadsheet_id() -> None:
    with pytest.raises(GoogleSheetsConfigError, match="GOOGLE_SHEETS_SPREADSHEET_ID"):
        read_sheet_values(
            spreadsheet_id="",
            sheet_range="Availability!A:H",
            credentials_path="unused-in-test.json",
            service=FakeService(FakeValues()),
        )


def test_preview_endpoint_returns_parsed_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.api.v1 import google_sheets

    def fake_read_sheet_values(
        spreadsheet_id: str,
        sheet_range: str,
        credentials_path: str,
    ) -> list[list[str]]:
        return [
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
            ["E001", "Sara Ahmed", "08:00 - 16:00", "N/A", "N/A", "N/A", "N/A", "N/A"],
        ]

    monkeypatch.setattr(google_sheets, "read_sheet_values", fake_read_sheet_values)

    client = TestClient(app)
    response = client.get("/api/v1/google-sheets/availability/preview?week_start=2026-06-08")

    assert response.status_code == 200
    assert response.json() == {
        "rows": [
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "monday",
                "work_date": "2026-06-08",
                "start_time": "08:00:00",
                "end_time": "16:00:00",
                "availability_type": "available",
                "notes": None,
            },
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "tuesday",
                "work_date": "2026-06-09",
                "start_time": None,
                "end_time": None,
                "availability_type": "unavailable",
                "notes": None,
            },
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "wednesday",
                "work_date": "2026-06-10",
                "start_time": None,
                "end_time": None,
                "availability_type": "unavailable",
                "notes": None,
            },
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "thursday",
                "work_date": "2026-06-11",
                "start_time": None,
                "end_time": None,
                "availability_type": "unavailable",
                "notes": None,
            },
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "friday",
                "work_date": "2026-06-12",
                "start_time": None,
                "end_time": None,
                "availability_type": "unavailable",
                "notes": None,
            },
            {
                "row_number": 2,
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "weekday": "saturday",
                "work_date": "2026-06-13",
                "start_time": None,
                "end_time": None,
                "availability_type": "unavailable",
                "notes": None,
            }
        ],
        "errors": [],
        "row_count": 6,
        "error_count": 0,
    }


def test_preview_endpoint_reports_missing_configuration() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/google-sheets/availability/preview?week_start=2026-06-08")

    assert response.status_code == 400
    assert response.json()["detail"] == "GOOGLE_SHEETS_SPREADSHEET_ID must be configured."


def test_preview_endpoint_requires_monday_week_start() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/google-sheets/availability/preview?week_start=2026-06-09")

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
