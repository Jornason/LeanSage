"""SEARCH S01: Chinese query is accepted and returns results."""
import pytest


@pytest.mark.search
def test_search_chinese_query(client, admin_headers):
    """S01: Chinese query is accepted and returns results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "自然数加法交换律", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert len(r.json()["data"]["results"]) >= 1
