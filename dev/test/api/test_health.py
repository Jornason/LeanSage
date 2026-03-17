"""Health check tests — HEALTH-01 to HEALTH-04."""
import pytest


@pytest.mark.smoke
def test_health_returns_200(client):
    r = client.get("/health")
    assert r.status_code == 200


@pytest.mark.smoke
def test_health_status_healthy(client):
    r = client.get("/health")
    assert r.json()["status"] == "healthy"


@pytest.mark.smoke
def test_health_environment_production(client):
    r = client.get("/health")
    assert r.json()["environment"] == "production"


@pytest.mark.smoke
def test_root_returns_200(client):
    r = client.get("/")
    assert r.status_code == 200


def test_health_has_version(client):
    r = client.get("/health")
    assert "version" in r.json()
