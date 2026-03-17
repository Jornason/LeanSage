"""Smoke: user profile endpoint accessible with valid token."""
import pytest


@pytest.mark.smoke
def test_profile_accessible(client, admin_headers):
    r = client.get("/v1/user/profile", headers=admin_headers)
    assert r.status_code == 200
