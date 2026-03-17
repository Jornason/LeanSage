"""SEARCH S05: Query longer than 500 characters is rejected with 422."""
import pytest


@pytest.mark.search
def test_search_overlong_query_returns_422(client, admin_headers):
    """S05: Query > 500 characters is rejected."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "x" * 501, "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 422
