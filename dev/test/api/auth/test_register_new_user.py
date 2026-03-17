"""AUTH A02: Valid registration creates account and returns token."""
import random
import pytest


@pytest.mark.auth
def test_register_new_user(client):
    """A02: Valid registration creates account and returns token."""
    email = f"reg_{random.randint(10000, 99999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "SecurePass99!", "display_name": "Tester"
    })
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "access_token" in r.json()["data"]
