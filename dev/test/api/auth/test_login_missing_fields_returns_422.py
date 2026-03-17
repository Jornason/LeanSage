"""AUTH: Login with missing fields returns 422."""
import pytest


@pytest.mark.auth
def test_login_missing_fields_returns_422(client):
    r = client.post("/v1/auth/login", json={"email": "admin@leanprove.ai"})
    assert r.status_code == 422
