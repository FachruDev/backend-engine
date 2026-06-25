from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_api_metadata() -> None:
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "AI Scheduler Engine"
    assert data["version"] == "0.1.0"


def test_health_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_versioned_health_returns_healthy_status() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
