"""AUTH: Admin login returns 200 with access_token and admin role."""
import pytest


@pytest.mark.smoke
@pytest.mark.auth
def test_admin_login_success(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.status_code == 200
    data = r.json()["data"]
    assert "access_token" in data
    assert data["user"]["role"] == "admin"
