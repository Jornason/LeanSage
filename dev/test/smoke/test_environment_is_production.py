"""Smoke: health endpoint reports production environment."""
import pytest


@pytest.mark.smoke
def test_environment_is_production(client):
    r = client.get("/health")
    assert r.json()["environment"] == "production"
