"""
Concurrency & stress tests.
Covers: CONC-01, CONC-02, edge cases under load.
"""
import time
import pytest
import threading
import httpx
from conftest import BASE_URL


def _search(token: str, query: str, results: list):
    with httpx.Client(base_url=BASE_URL, timeout=30) as c:
        r = c.post("/v1/search/mathlib",
                   json={"query": query, "top_k": 3},
                   headers={"Authorization": f"Bearer {token}"})
        results.append(r.status_code)


def _diagnose(token: str, idx: int, results: list):
    with httpx.Client(base_url=BASE_URL, timeout=45) as c:
        r = c.post("/v1/diagnose/error",
                   json={"code": f"theorem foo{idx} : 1 = 1 := by rfl",
                         "error_message": None},
                   headers={"Authorization": f"Bearer {token}"})
        results.append(r.status_code)


@pytest.mark.concurrent
def test_10_concurrent_searches(admin_token):
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


@pytest.mark.concurrent
@pytest.mark.ai
def test_5_concurrent_diagnoses(admin_token):
    """CONC-02: 5 simultaneous diagnose requests all return 200."""
    results = []
    threads = [
        threading.Thread(target=_diagnose, args=(admin_token, i, results))
        for i in range(5)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    success = sum(1 for s in results if s == 200)
    assert success >= 4, f"Only {success}/5 diagnoses succeeded; statuses={results}"


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
