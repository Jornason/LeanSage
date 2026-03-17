"""SEARCH: Search without token returns 401 or 403."""
import pytest


@pytest.mark.search
def test_search_requires_auth(client):
    """Search without token returns 401/403."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 5})
    assert r.status_code in (401, 403)
