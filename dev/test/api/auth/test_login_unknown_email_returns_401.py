"""AUTH: Unknown email returns 401."""
import pytest


@pytest.mark.auth
def test_login_unknown_email_returns_401(client):
    r = client.post("/v1/auth/login", json={
        "email": "nobody@nowhere.com", "password": "password123"
    })
    assert r.status_code == 401
