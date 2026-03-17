"""USER-04: Usage response contains quota-related fields."""
import pytest


@pytest.mark.user
def test_user_usage_has_quota_fields(client, admin_headers):
    """USER-04: Usage response contains quota-related fields."""
    r = client.get("/v1/user/usage", headers=admin_headers)
    text = str(r.json()["data"]).lower()
    assert any(kw in text for kw in ("quota", "limit", "used", "searches"))
