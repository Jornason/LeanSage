"""Smoke: user usage endpoint accessible with valid token."""
import pytest


@pytest.mark.smoke
def test_usage_accessible(client, admin_headers):
    r = client.get("/v1/user/usage", headers=admin_headers)
    assert r.status_code == 200
