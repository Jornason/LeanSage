"""SEARCH: top_k=20 (max allowed) returns at most 20 results."""
import pytest


@pytest.mark.search
def test_search_top_k_max(client, admin_headers):
    """top_k=20 (max allowed) returns at most 20 results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "theorem", "top_k": 20},
                    headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["results"]) <= 20
