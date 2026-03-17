"""SEARCH: Each result contains theorem_name and type_signature."""
import pytest


@pytest.mark.search
def test_search_result_fields(client, admin_headers):
    """Each result contains theorem_name and type_signature."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "Nat.add_comm", "top_k": 1},
                    headers=admin_headers)
    assert r.status_code == 200
    results = r.json()["data"]["results"]
    if results:
        item = results[0]
        assert "theorem_name" in item
        assert "type_signature" in item
