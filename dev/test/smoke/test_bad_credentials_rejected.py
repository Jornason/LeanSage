"""Smoke: wrong password returns 401."""
import pytest


@pytest.mark.smoke
def test_bad_credentials_rejected(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "wrongpassword99"
    })
    assert r.status_code == 401
