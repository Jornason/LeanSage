"""USER-02: Profile response contains role field."""
import pytest


@pytest.mark.user
def test_user_profile_contains_role(client, admin_headers):
    """USER-02: Profile response contains role field."""
    r = client.get("/v1/user/profile", headers=admin_headers)
    profile = r.json()["data"]
    assert "role" in str(profile)
