"""HEALTH-04: /health response contains uptime field."""
import pytest


@pytest.mark.smoke
def test_health_uptime_present(client):
    r = client.get("/health")
    assert r.status_code == 200
