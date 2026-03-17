"""USER-01: Admin can retrieve their profile."""
import pytest


@pytest.mark.user
def test_user_get_profile(client, admin_headers):
    """USER-01: Admin can retrieve their profile."""
    r = client.get("/v1/user/profile", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
