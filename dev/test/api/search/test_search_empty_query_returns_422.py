"""SEARCH S04: Empty query is rejected with 422."""
import pytest


@pytest.mark.search
def test_search_empty_query_returns_422(client, admin_headers):
    """S04: Empty query is rejected."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 422
