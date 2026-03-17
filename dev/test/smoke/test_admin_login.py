"""Smoke: admin credentials produce a valid access token."""
import pytest


@pytest.mark.smoke
def test_admin_login(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]
