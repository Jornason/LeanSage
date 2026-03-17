"""SEARCH: top_k=0 violates ge=1 constraint, returns 422."""
import pytest


@pytest.mark.search
def test_search_top_k_min(client, admin_headers):
    """top_k=0 violates ge=1 constraint."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 0},
                    headers=admin_headers)
    assert r.status_code == 422
