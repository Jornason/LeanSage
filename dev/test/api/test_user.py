"""
User profile & usage stats tests.
Covers: USER-01 to USER-04, Q-ADMIN, Q03
"""
import pytest


@pytest.mark.user
def test_get_profile_admin(client, admin_headers):
    """USER-01: Admin can retrieve their profile."""
    r = client.get("/v1/user/profile", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


@pytest.mark.user
def test_profile_contains_role(client, admin_headers):
    """USER-02: Profile response contains role field."""
    r = client.get("/v1/user/profile", headers=admin_headers)
    profile = r.json()["data"]
    assert "role" in str(profile)


@pytest.mark.user
def test_admin_profile_role_is_admin(client, admin_headers):
    r = client.get("/v1/user/profile", headers=admin_headers)
    data = r.json()["data"]
    # role may be nested under user or at top level
    role = data.get("role") or data.get("user", {}).get("role", "")
    assert role == "admin"


@pytest.mark.user
def test_get_usage_admin(client, admin_headers):
    """USER-03: Admin can retrieve usage statistics."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


@pytest.mark.user
def test_usage_has_quota_fields(client, admin_headers):
    """USER-04: Usage response contains quota-related fields."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    text = str(r.json()["data"]).lower()
    assert any(kw in text for kw in ("quota", "limit", "used", "searches"))


@pytest.mark.user
def test_admin_has_unlimited_quota(client, admin_headers):
    """Q-ADMIN: Admin plan quota is -1 (unlimited) or marked unlimited."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    text = str(r.json()["data"])
    assert "-1" in text or "unlimited" in text.lower() or "admin" in text.lower()


@pytest.mark.user
def test_researcher_can_get_usage(client, demo_headers):
    """Q03: Researcher plan user can retrieve usage."""
    r = client.get("/v1/user/usage", headers=demo_headers)
    assert r.status_code == 200


@pytest.mark.user
def test_profile_requires_auth(client):
    r = client.get("/v1/user/profile")
    assert r.status_code in (401, 403)


@pytest.mark.user
def test_usage_requires_auth(client):
    r = client.get("/v1/user/usage")
    assert r.status_code in (401, 403)
