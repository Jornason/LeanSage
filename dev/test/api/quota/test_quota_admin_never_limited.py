"""QUOTA: Admin plan searches are always allowed regardless of usage count."""
import pytest


@pytest.mark.quota
def test_quota_admin_never_limited(client, admin_headers):
    """Admin plan searches are always allowed regardless of usage count."""
    for _ in range(3):
        r = client.post("/v1/search/mathlib",
                        json={"query": "addition natural numbers", "top_k": 1},
                        headers=admin_headers)
        assert r.status_code == 200, f"Admin was quota-limited: {r.json()}"
