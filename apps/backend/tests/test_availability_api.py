from datetime import date, time

from fastapi.testclient import TestClient

from app.api.v1 import availability as availability_api
from app.api.v1 import employees as employees_api
from app.db.enums import AvailabilityType
from app.db.models import Employee
from app.db.session import get_db
from app.main import app
from app.services.availability_queries import AvailabilityListItem


async def fake_get_db():
    yield object()


def test_get_employees_returns_stored_employees(monkeypatch) -> None:
    employee = Employee(
        employee_code="E001",
        full_name="Sara Ahmed",
        active=True,
        employment_type=None,
        weekly_hours_target=None,
        max_weekly_hours=None,
    )
    employee.id = "employee-1"

    async def fake_list_employees(db):
        return [employee]

    monkeypatch.setattr(employees_api, "list_employees", fake_list_employees)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/employees")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "rows": [
            {
                "id": "employee-1",
                "employee_code": "E001",
                "full_name": "Sara Ahmed",
                "active": True,
                "employment_type": None,
                "weekly_hours_target": None,
                "max_weekly_hours": None,
            }
        ],
        "row_count": 1,
    }


def test_get_week_availability_returns_stored_rows(monkeypatch) -> None:
    rows = [
        AvailabilityListItem(
            id="availability-1",
            employee_id="employee-1",
            employee_code="E001",
            employee_name="Sara Ahmed",
            work_date=date(2026, 6, 8),
            start_time=time(8, 0),
            end_time=time(16, 0),
            availability_type=AvailabilityType.AVAILABLE,
            notes=None,
        )
    ]

    async def fake_list_week_availability(db, week_start):
        return rows

    monkeypatch.setattr(
        availability_api,
        "list_week_availability",
        fake_list_week_availability,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/availability?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-06-08",
        "week_end": "2026-06-13",
        "rows": [
            {
                "id": "availability-1",
                "employee_id": "employee-1",
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "work_date": "2026-06-08",
                "start_time": "08:00:00",
                "end_time": "16:00:00",
                "availability_type": "available",
                "notes": None,
            }
        ],
        "row_count": 1,
    }


def test_get_week_availability_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/availability?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."


def test_get_availability_summary_returns_counts_and_hours(monkeypatch) -> None:
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
    ]

    async def fake_list_week_availability(db, week_start):
        return rows

    monkeypatch.setattr(
        availability_api,
        "list_week_availability",
        fake_list_week_availability,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/availability/summary?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-06-08",
        "week_end": "2026-06-13",
        "days": [
            {
                "weekday": "monday",
                "work_date": "2026-06-08",
                "available_employee_count": 1,
                "unavailable_employee_count": 1,
                "available_hours": 8.0,
            },
            {
                "weekday": "tuesday",
                "work_date": "2026-06-09",
                "available_employee_count": 0,
                "unavailable_employee_count": 0,
                "available_hours": 0.0,
            },
            {
                "weekday": "wednesday",
                "work_date": "2026-06-10",
                "available_employee_count": 0,
                "unavailable_employee_count": 0,
                "available_hours": 0.0,
            },
            {
                "weekday": "thursday",
                "work_date": "2026-06-11",
                "available_employee_count": 0,
                "unavailable_employee_count": 0,
                "available_hours": 0.0,
            },
            {
                "weekday": "friday",
                "work_date": "2026-06-12",
                "available_employee_count": 0,
                "unavailable_employee_count": 0,
                "available_hours": 0.0,
            },
            {
                "weekday": "saturday",
                "work_date": "2026-06-13",
                "available_employee_count": 0,
                "unavailable_employee_count": 0,
                "available_hours": 0.0,
            },
        ],
        "employees": [
            {
                "employee_id": "employee-1",
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "available_hours": 8.0,
            },
            {
                "employee_id": "employee-2",
                "employee_code": "E002",
                "employee_name": "John Doe",
                "available_hours": 0.0,
            },
        ],
        "day_count": 6,
        "employee_count": 2,
    }


def test_get_availability_summary_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/availability/summary?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
