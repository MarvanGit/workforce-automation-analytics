from datetime import date, time

from fastapi.testclient import TestClient

from app.api.v1 import shifts as shifts_api
from app.db.models import ShiftTemplate
from app.db.session import get_db
from app.main import app
from app.services.shift_queries import ShiftDemandListItem


async def fake_get_db():
    yield object()


def test_get_shift_templates_returns_stored_templates(monkeypatch) -> None:
    template = ShiftTemplate(
        name="Morning",
        start_time=time(8, 0),
        end_time=time(16, 0),
        duration_minutes=480,
        is_overnight=False,
        active=True,
    )
    template.id = "template-1"

    async def fake_list_shift_templates(db):
        return [template]

    monkeypatch.setattr(shifts_api, "list_shift_templates", fake_list_shift_templates)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/shift-templates")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "rows": [
            {
                "id": "template-1",
                "name": "Morning",
                "start_time": "08:00:00",
                "end_time": "16:00:00",
                "duration_minutes": 480,
                "is_overnight": False,
                "active": True,
            }
        ],
        "row_count": 1,
    }


def test_create_shift_template_returns_created_template(monkeypatch) -> None:
    template = ShiftTemplate(
        name="Morning",
        start_time=time(9, 0),
        end_time=time(17, 0),
        duration_minutes=480,
        is_overnight=False,
        active=True,
    )
    template.id = "template-1"

    async def fake_create_shift_template(db, name, start_time, end_time, active):
        assert name == "Morning"
        assert start_time == time(9, 0)
        assert end_time == time(17, 0)
        assert active is True
        return template

    monkeypatch.setattr(
        shifts_api,
        "create_shift_template",
        fake_create_shift_template,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/shift-templates",
            json={
                "name": "Morning",
                "start_time": "09:00",
                "end_time": "17:00",
                "active": True,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "id": "template-1",
        "name": "Morning",
        "start_time": "09:00:00",
        "end_time": "17:00:00",
        "duration_minutes": 480,
        "is_overnight": False,
        "active": True,
    }


def test_create_shift_template_returns_validation_error(monkeypatch) -> None:
    async def fake_create_shift_template(db, name, start_time, end_time, active):
        raise ValueError("shift template name already exists.")

    monkeypatch.setattr(
        shifts_api,
        "create_shift_template",
        fake_create_shift_template,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/shift-templates",
            json={
                "name": "Morning",
                "start_time": "09:00",
                "end_time": "17:00",
                "active": True,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "shift template name already exists."


def test_get_shift_demand_returns_week_rows(monkeypatch) -> None:
    rows = [
        ShiftDemandListItem(
            id="demand-1",
            demand_date=date(2026, 6, 8),
            shift_template_id="template-1",
            shift_template_name="Morning",
            shift_start_time=time(8, 0),
            shift_end_time=time(16, 0),
            required_employee_count=3,
            notes="Busy morning",
        )
    ]

    async def fake_list_week_shift_demand(db, week_start):
        return rows

    monkeypatch.setattr(
        shifts_api,
        "list_week_shift_demand",
        fake_list_week_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/shift-demand?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-06-08",
        "week_end": "2026-06-13",
        "rows": [
            {
                "id": "demand-1",
                "demand_date": "2026-06-08",
                "weekday": "monday",
                "shift_template_id": "template-1",
                "shift_template_name": "Morning",
                "shift_start_time": "08:00:00",
                "shift_end_time": "16:00:00",
                "required_employee_count": 3,
                "notes": "Busy morning",
            }
        ],
        "row_count": 1,
    }


def test_create_shift_demand_returns_created_row(monkeypatch) -> None:
    row = ShiftDemandListItem(
        id="demand-1",
        demand_date=date(2026, 6, 8),
        shift_template_id="template-1",
        shift_template_name="Morning",
        shift_start_time=time(9, 0),
        shift_end_time=time(17, 0),
        required_employee_count=2,
        notes=None,
    )

    async def fake_create_shift_demand(
        db,
        demand_date,
        shift_template_id,
        required_employee_count,
        notes,
    ):
        assert demand_date == date(2026, 6, 8)
        assert shift_template_id == "template-1"
        assert required_employee_count == 2
        assert notes is None
        return row

    monkeypatch.setattr(
        shifts_api,
        "create_shift_demand",
        fake_create_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/shift-demand",
            json={
                "demand_date": "2026-06-08",
                "shift_template_id": "template-1",
                "required_employee_count": 2,
                "notes": None,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json() == {
        "id": "demand-1",
        "demand_date": "2026-06-08",
        "weekday": "monday",
        "shift_template_id": "template-1",
        "shift_template_name": "Morning",
        "shift_start_time": "09:00:00",
        "shift_end_time": "17:00:00",
        "required_employee_count": 2,
        "notes": None,
    }


def test_create_shift_demand_returns_validation_error(monkeypatch) -> None:
    async def fake_create_shift_demand(
        db,
        demand_date,
        shift_template_id,
        required_employee_count,
        notes,
    ):
        raise ValueError("shift_template_id was not found.")

    monkeypatch.setattr(
        shifts_api,
        "create_shift_demand",
        fake_create_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/shift-demand",
            json={
                "demand_date": "2026-06-08",
                "shift_template_id": "missing-template",
                "required_employee_count": 2,
                "notes": None,
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "shift_template_id was not found."


def test_delete_shift_demand_returns_no_content(monkeypatch) -> None:
    async def fake_delete_shift_demand(db, demand_id):
        assert demand_id == "demand-1"
        return True

    monkeypatch.setattr(
        shifts_api,
        "delete_shift_demand",
        fake_delete_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.delete("/api/v1/shift-demand/demand-1")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 204
    assert response.content == b""


def test_delete_shift_demand_returns_not_found(monkeypatch) -> None:
    async def fake_delete_shift_demand(db, demand_id):
        return False

    monkeypatch.setattr(
        shifts_api,
        "delete_shift_demand",
        fake_delete_shift_demand,
    )
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.delete("/api/v1/shift-demand/missing-demand")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json()["detail"] == "shift demand was not found."


def test_get_shift_demand_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/shift-demand?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
