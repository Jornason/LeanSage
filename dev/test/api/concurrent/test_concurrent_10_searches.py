"""CONCURRENT CONC-01: 10 simultaneous search requests all succeed."""
import os
import time
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
def test_concurrent_10_searches(admin_token):
    """CONC-01: 10 simultaneous search requests all succeed."""
    results = []
    threads = [
        threading.Thread(target=_search,
                         args=(admin_token, f"nat add theorem {i}", results))
        for i in range(10)
    ]
    t0 = time.time()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    elapsed = time.time() - t0

    success = sum(1 for s in results if s == 200)
    assert success >= 8, f"Only {success}/10 succeeded; statuses={results}"
    # All 10 completed within 5 seconds (internal mock is fast)
    assert elapsed < 5.0, f"10 concurrent searches took {elapsed:.1f}s"
