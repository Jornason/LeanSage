"""SEARCH S06: Two identical queries both succeed (cache hit)."""
import pytest


@pytest.mark.search
def test_search_cached_result(client, admin_headers):
    """S06: Two identical queries both succeed (cache hit)."""
    q = {"query": "continuous function real analysis", "top_k": 5}
    r1 = client.post("/v1/search/mathlib", json=q, headers=admin_headers)
    r2 = client.post("/v1/search/mathlib", json=q, headers=admin_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
