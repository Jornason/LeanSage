"""USER: Admin profile role is 'admin'."""
import pytest


@pytest.mark.user
def test_user_admin_role(client, admin_headers):
    r = client.get("/v1/user/profile", headers=admin_headers)
    data = r.json()["data"]
    # role may be nested under user or at top level
    role = data.get("role") or data.get("user", {}).get("role", "")
    assert role == "admin"
