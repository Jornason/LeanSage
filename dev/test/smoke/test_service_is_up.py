"""Smoke: service health endpoint returns 200 and healthy status."""
import pytest


@pytest.mark.smoke
def test_service_is_up(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"
