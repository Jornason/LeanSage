"""Smoke: basic search query returns at least one result."""
import pytest


@pytest.mark.smoke
def test_search_returns_results(client, admin_headers):
    r = client.post("/v1/search/mathlib",
                    json={"query": "commutativity addition", "top_k": 3},
                    headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["results"]) >= 1
