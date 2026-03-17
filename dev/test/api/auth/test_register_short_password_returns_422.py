"""AUTH AU05: Password shorter than 8 characters is rejected."""
import random
import pytest


@pytest.mark.auth
def test_register_short_password_returns_422(client):
    """AU05: Password < 8 characters is rejected."""
    email = f"short_{random.randint(1, 9999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "123", "display_name": "X"
    })
    assert r.status_code == 422
