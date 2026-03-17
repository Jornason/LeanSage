"""AUTH AUTH-04: No token at all is rejected with 401 or 403."""
import pytest


@pytest.mark.auth
def test_missing_token_returns_401_or_403(client):
    """AUTH-04: No token at all is rejected."""
    r = client.get("/v1/user/profile")
    assert r.status_code in (401, 403)
