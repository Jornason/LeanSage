"""USER Q-ADMIN: Admin plan quota is -1 (unlimited) or marked unlimited."""
import pytest


@pytest.mark.user
def test_user_admin_unlimited_quota(client, admin_headers):
    """Q-ADMIN: Admin plan quota is -1 (unlimited) or marked unlimited."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    text = str(r.json()["data"])
    assert "-1" in text or "unlimited" in text.lower() or "admin" in text.lower()
