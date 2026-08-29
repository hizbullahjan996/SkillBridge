from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "SkillBridge API"
    assert "version" in data


def test_health_db_check():
    response = client.get("/api/health/db")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ok", "error")
    assert data["database"] in ("connected", "disconnected")


def test_invalid_route():
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_docs_endpoint():
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_endpoint():
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "paths" in data
    assert "/api/health" in data["paths"]
    assert "/api/health/db" in data["paths"]
