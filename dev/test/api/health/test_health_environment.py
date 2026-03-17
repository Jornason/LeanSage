"""HEALTH-02: /health reports production environment."""
import pytest


@pytest.mark.smoke
def test_health_environment(client):
    r = client.get("/health")
    assert r.json()["environment"] == "production"
