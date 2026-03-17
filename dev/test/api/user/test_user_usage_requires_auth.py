"""USER: Usage without token returns 401 or 403."""
import pytest


@pytest.mark.user
def test_user_usage_requires_auth(client):
    r = client.get("/v1/user/usage")
    assert r.status_code in (401, 403)
