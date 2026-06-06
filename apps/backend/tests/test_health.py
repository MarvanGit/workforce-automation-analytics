from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_service_status() -> None:
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "Workforce Automation Analytics",
        "environment": "local",
    }


def test_cors_allows_local_127_frontend() -> None:
    client = TestClient(app)

    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://127.0.0.1:4200",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:4200"
