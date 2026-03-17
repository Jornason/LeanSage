"""AUTH A01: /auth/demo provides instant token without credentials."""
import pytest


@pytest.mark.smoke
@pytest.mark.auth
def test_demo_endpoint_returns_token(client):
    """A01: /auth/demo provides instant token without credentials."""
    r = client.post("/v1/auth/demo")
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]
