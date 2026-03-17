"""AUTH AU02: Second registration with same email returns 409."""
import random
import pytest


@pytest.mark.auth
def test_register_duplicate_email_returns_409(client):
    """AU02: Second registration with same email returns 409."""
    email = f"dup_{random.randint(10000, 99999)}@test-leansage.com"
    payload = {"email": email, "password": "SecurePass99!", "display_name": "Tester"}
    client.post("/v1/auth/register", json=payload)
    r = client.post("/v1/auth/register", json=payload)
    assert r.status_code == 409
