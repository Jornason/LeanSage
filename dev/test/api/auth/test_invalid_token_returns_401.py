"""AUTH AU03: Malformed/expired token is rejected with 401."""
import pytest


@pytest.mark.auth
def test_invalid_token_returns_401(client):
    """AU03: Malformed / expired token is rejected."""
    r = client.get("/v1/user/profile",
                   headers={"Authorization": "Bearer invalid.jwt.token"})
    assert r.status_code == 401
