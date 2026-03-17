"""HEALTH-03: /health response contains version field."""
import pytest


def test_health_version_present(client):
    r = client.get("/health")
    assert "version" in r.json()
