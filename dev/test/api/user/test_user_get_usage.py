"""USER-03: Admin can retrieve usage statistics."""
import pytest


@pytest.mark.user
def test_user_get_usage(client, admin_headers):
    """USER-03: Admin can retrieve usage statistics."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
