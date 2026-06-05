from datetime import date, time

from fastapi.testclient import TestClient

from app.api.v1 import scheduling as scheduling_api
from app.db.enums import AvailabilityType, SchedulingRunStatus
from app.db.session import get_db
from app.main import app
from app.services.availability_queries import AvailabilityListItem
from app.services.scheduling_storage import SavedScheduledShift, SavedScheduleRun
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


def test_post_schedule_run_returns_saved_run(monkeypatch) -> None:
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
    saved_run = SavedScheduleRun(
        id="run-1",
        start_date=date(2026, 6, 8),
        end_date=date(2026, 6, 13),
        status=SchedulingRunStatus.COMPLETED,
        scheduled_shifts=[
            SavedScheduledShift(
                id="scheduled-shift-1",
                employee_id="employee-1",
                employee_code="E001",
                employee_name="Sara Ahmed",
                shift_date=date(2026, 6, 8),
                shift_template_id="template-1",
                shift_template_name="Morning",
                start_datetime="2026-06-08T09:00:00+00:00",
                end_datetime="2026-06-08T17:00:00+00:00",
            )
        ],
        warnings=[],
    )

    async def fake_list_week_availability(db, week_start):
        return availability_rows

    async def fake_list_week_absences(db, week_start):
        return []

    async def fake_list_week_shift_demand(db, week_start):
        return demand_rows

    async def fake_save_schedule_preview(db, preview):
        assert preview.week_start == date(2026, 6, 8)
        assert len(preview.shifts) == 1
        return saved_run

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
    monkeypatch.setattr(
        scheduling_api,
        "save_schedule_preview",
        fake_save_schedule_preview,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post("/api/v1/scheduling/runs?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "id": "run-1",
        "start_date": "2026-06-08",
        "end_date": "2026-06-13",
        "status": "completed",
        "scheduled_shifts": [
            {
                "id": "scheduled-shift-1",
                "employee_id": "employee-1",
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "shift_date": "2026-06-08",
                "shift_template_id": "template-1",
                "shift_template_name": "Morning",
                "start_datetime": "2026-06-08T09:00:00Z",
                "end_datetime": "2026-06-08T17:00:00Z",
            }
        ],
        "scheduled_shift_count": 1,
        "warnings": [],
        "warning_count": 0,
    }


def test_post_schedule_run_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post("/api/v1/scheduling/runs?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
