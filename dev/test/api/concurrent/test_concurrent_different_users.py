"""CONCURRENT: Two different users can search simultaneously without interference."""
import os
import threading
import pytest
import httpx

BASE_URL = os.environ.get("BASE_URL", "http://localhost:9019")


def _search(token: str, query: str, results: list):
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        r = c.post("/v1/search/mathlib",
                   json={"query": query, "top_k": 3},
                   headers={"Authorization": f"Bearer {token}"})
        results.append(r.status_code)


@pytest.mark.concurrent
def test_concurrent_different_users(demo_direct_token, admin_token):
    """Two different users can search simultaneously without interference."""
    results = []
    threads = [
        threading.Thread(target=_search,
                         args=(admin_token, "ring commutativity", results)),
        threading.Thread(target=_search,
                         args=(demo_direct_token, "induction natural", results)),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert all(s == 200 for s in results), f"Statuses: {results}"
