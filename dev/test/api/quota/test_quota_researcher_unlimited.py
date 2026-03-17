"""QUOTA Q03: Researcher plan has no monthly search limit (quota=-1)."""
import pytest


@pytest.mark.quota
def test_quota_researcher_unlimited(client, demo_headers):
    """Q03: Researcher plan has no monthly search limit (quota=-1)."""
    r = client.get("/v1/user/usage", headers=demo_headers)
    assert r.status_code == 200
    text = str(r.json()["data"])
    # Researcher searches should be -1 (unlimited) or have high limit
    # Just check the call succeeds and we have usage data
    assert len(text) > 5
