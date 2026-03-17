"""SEARCH S07: top_k=3 returns at most 3 results."""
import pytest


@pytest.mark.search
def test_search_top_k_respected(client, admin_headers):
    """S07: top_k=3 returns at most 3 results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "natural number induction", "top_k": 3},
                    headers=admin_headers)
    assert r.status_code == 200
    results = r.json()["data"]["results"]
    assert len(results) <= 3
