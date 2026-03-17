"""AUTH: Registration without display_name returns 422."""
import random
import pytest


@pytest.mark.auth
def test_register_missing_display_name_returns_422(client):
    email = f"nodname_{random.randint(1, 9999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "SecurePass99!"
    })
    assert r.status_code == 422
