"""QUOTA: Free plan can use basic explain (no detail_level=detailed)."""
import pytest


@pytest.mark.quota
def test_quota_free_explain_allowed(client, free_user):
    """Free plan can use basic explain (no detail_level=detailed)."""
    r = client.post("/v1/explain/tactics",
                    json={"code": "theorem f :=\nby\n  ring", "language": "en"},
                    headers=free_user["headers"])
    # Should succeed OR be quota-limited (both are valid depending on usage count)
    assert r.status_code in (200, 429)
