"""AUTH: Login response token_type is bearer."""
import pytest


@pytest.mark.auth
def test_token_type_is_bearer(client, admin_token):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.json()["data"]["token_type"].lower() == "bearer"
