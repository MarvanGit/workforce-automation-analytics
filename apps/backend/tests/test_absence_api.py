from datetime import date

from fastapi.testclient import TestClient

from app.api.v1 import absences as absences_api
from app.db.enums import AbsenceType
from app.db.session import get_db
from app.main import app
from app.services.absence_queries import AbsenceListItem


async def fake_get_db():
    yield object()


def test_get_week_absences_returns_stored_rows(monkeypatch) -> None:
    rows = [
        AbsenceListItem(
            id="absence-1",
            employee_id="employee-1",
            employee_code="E001",
            employee_name="Sara Ahmed",
            start_date=date(2026, 6, 9),
            end_date=date(2026, 6, 10),
            absence_type=AbsenceType.VACATION,
            notes="Approved vacation",
        )
    ]

    async def fake_list_week_absences(db, week_start):
        return rows

    monkeypatch.setattr(absences_api, "list_week_absences", fake_list_week_absences)
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/absences?week_start=2026-06-08")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "week_start": "2026-06-08",
        "week_end": "2026-06-13",
        "rows": [
            {
                "id": "absence-1",
                "employee_id": "employee-1",
                "employee_code": "E001",
                "employee_name": "Sara Ahmed",
                "start_date": "2026-06-09",
                "end_date": "2026-06-10",
                "absence_type": "vacation",
                "notes": "Approved vacation",
            }
        ],
        "row_count": 1,
    }


def test_get_week_absences_requires_monday() -> None:
    app.dependency_overrides[get_db] = fake_get_db

    try:
        client = TestClient(app)
        response = client.get("/api/v1/absences?week_start=2026-06-09")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json()["detail"] == "week_start must be a Monday."
