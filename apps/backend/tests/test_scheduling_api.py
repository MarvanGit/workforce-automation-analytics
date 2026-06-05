from datetime import date, time

from fastapi.testclient import TestClient

from app.api.v1 import scheduling as scheduling_api
from app.db.enums import AvailabilityType
from app.db.session import get_db
from app.main import app
from app.services.availability_queries import AvailabilityListItem
from app.services.shift_queries import ShiftDemandListItem


async def fake_get_db():
    yield object()


def test_get_schedule_preview_returns_generated_assignments(monkeypatch) -> None:
    availability_rows = [
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
        )
    ]
    demand_rows = [
        ShiftDemandListItem(
            id="demand-1",
            demand_date=date(2026, 6, 8),
            shift_template_id="template-1",
            shift_template_name="Morning",
            shift_start_time=time(9, 0),
            shift_end_time=time(17, 0),
            required_employee_count=1,
            notes=None,
        )
    ]

    async def fake_list_week_availability(db, week_start):
        return availability_rows

    async def fake_list_week_absences(db, week_start):
        return []

    async def fake_list_week_shift_demand(db, week_start):
        return demand_rows

    monkeypatch.setattr(
        scheduling_api,
        "list_week_availability",
        fake_list_week_availability,
    )
    monkeypatch.setattr(
        scheduling_api,
        "list_week_absences",
        fake_list_week_absences,
    )
    monkeypatch.setattr(
        scheduling_api,
        "list_week_shift_demand",
        fake_list_week_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/scheduling/preview?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-06-08",
        "week_end": "2026-06-13",
        "shifts": [
            {
                "demand_id": "demand-1",
                "demand_date": "2026-06-08",
                "weekday": "monday",
                "shift_template_id": "template-1",
                "shift_template_name": "Morning",
                "shift_start_time": "09:00:00",
                "shift_end_time": "17:00:00",
                "required_employee_count": 1,
                "assigned_employees": [
                    {
                        "employee_id": "employee-1",
                        "employee_code": "E001",
                        "employee_name": "Sara Ahmed",
                    }
                ],
                "missing_employee_count": 0,
            }
        ],
        "shift_count": 1,
        "assignment_count": 1,
        "warnings": [],
        "warning_count": 0,
    }


def test_get_schedule_preview_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/scheduling/preview?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
