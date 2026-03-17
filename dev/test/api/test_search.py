"""
Mathlib search tests.
Covers: S01-S07
"""
import pytest


@pytest.mark.smoke
@pytest.mark.search
def test_search_returns_results(client, admin_headers):
    """S02: Basic English query returns results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "commutativity of addition", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    results = r.json()["data"]["results"]
    assert len(results) >= 1


@pytest.mark.search
def test_search_chinese_query(client, admin_headers):
    """S01: Chinese query is accepted and returns results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "自然数加法交换律", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert len(r.json()["data"]["results"]) >= 1


@pytest.mark.search
def test_search_top_k_respected(client, admin_headers):
    """S07: top_k=3 returns at most 3 results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "natural number induction", "top_k": 3},
                    headers=admin_headers)
    assert r.status_code == 200
    results = r.json()["data"]["results"]
    assert len(results) <= 3


@pytest.mark.search
def test_search_top_k_max(client, admin_headers):
    """top_k=20 (max allowed) returns at most 20 results."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "theorem", "top_k": 20},
                    headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["results"]) <= 20


@pytest.mark.search
def test_search_empty_query_returns_422(client, admin_headers):
    """S04: Empty query is rejected."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "", "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.search
def test_search_overlong_query_returns_422(client, admin_headers):
    """S05: Query > 500 characters is rejected."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "x" * 501, "top_k": 5},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.search
def test_search_top_k_zero_returns_422(client, admin_headers):
    """top_k=0 violates ge=1 constraint."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 0},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.search
def test_search_top_k_over_max_returns_422(client, admin_headers):
    """top_k=21 violates le=20 constraint."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 21},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.search
def test_search_requires_auth(client):
    """Search without token returns 401/403."""
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 5})
    assert r.status_code in (401, 403)


@pytest.mark.search
def test_search_result_has_expected_fields(client, admin_headers):
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


@pytest.mark.search
def test_search_cache_second_call_succeeds(client, admin_headers):
    """S06: Two identical queries both succeed (cache hit)."""
    q = {"query": "continuous function real analysis", "top_k": 5}
    r1 = client.post("/v1/search/mathlib", json=q, headers=admin_headers)
    r2 = client.post("/v1/search/mathlib", json=q, headers=admin_headers)
    assert r1.status_code == 200
    assert r2.status_code == 200
