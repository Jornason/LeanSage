"""SEARCH S02: Basic English query returns results."""
import pytest


@pytest.mark.smoke
@pytest.mark.search
def test_search_english_query(client, admin_headers):
    """S02: Basic English query returns results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "commutativity of addition", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    results = r.json()["data"]["results"]
    assert len(results) >= 1
