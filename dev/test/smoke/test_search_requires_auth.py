"""Smoke: search without token returns 401 or 403."""
import pytest


@pytest.mark.smoke
def test_search_requires_auth(client):
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 3})
    assert r.status_code in (401, 403)
