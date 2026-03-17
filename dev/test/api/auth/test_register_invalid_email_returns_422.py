"""AUTH AU01: Non-email string rejected with 422."""
import pytest


@pytest.mark.auth
def test_register_invalid_email_returns_422(client):
    """AU01: Non-email string rejected with 422."""
    r = client.post("/v1/auth/register", json={
        "email": "not-an-email", "password": "SecurePass99!", "display_name": "X"
    })
    assert r.status_code == 422
