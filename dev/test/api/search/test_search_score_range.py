"""SEARCH: top_k=21 violates le=20 constraint, returns 422."""
import pytest


@pytest.mark.search
def test_search_score_range(client, admin_headers):
    """top_k=21 violates le=20 constraint."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 21},
                    headers=admin_headers)
    assert r.status_code == 422
