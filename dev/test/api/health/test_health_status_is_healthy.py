"""HEALTH-01: /health returns 200."""
import pytest


@pytest.mark.smoke
def test_health_status_is_healthy(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
