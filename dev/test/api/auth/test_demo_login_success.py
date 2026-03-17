"""AUTH: Demo login returns 200 with access_token."""
import pytest


@pytest.mark.smoke
@pytest.mark.auth
def test_demo_login_success(client):
    r = client.post("/v1/auth/login", json={
        "email": "demo@leanprove.ai", "password": "demo12345"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]
