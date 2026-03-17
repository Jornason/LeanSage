"""Smoke: /auth/demo endpoint returns access token without credentials."""
import pytest


@pytest.mark.smoke
def test_demo_auto_login(client):
    r = client.post("/v1/auth/demo")
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]
