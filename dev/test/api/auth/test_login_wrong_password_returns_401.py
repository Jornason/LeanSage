"""AUTH: Wrong password returns 401."""
import pytest


@pytest.mark.auth
def test_login_wrong_password_returns_401(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "wrongpassword99"
    })
    assert r.status_code == 401
