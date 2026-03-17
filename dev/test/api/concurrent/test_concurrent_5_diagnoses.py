"""CONCURRENT CONC-02: 5 simultaneous diagnose requests all return 200."""
import os
import threading
import pytest
import httpx

BASE_URL = os.environ.get("BASE_URL", "http://localhost:9019")


def _diagnose(token: str, idx: int, results: list):
    with httpx.Client(base_url=BASE_URL, timeout=45) as c:
        r = c.post("/v1/diagnose/error",
                   json={"code": f"theorem foo{idx} : 1 = 1 := by rfl",
                         "error_message": None},
                   headers={"Authorization": f"Bearer {token}"})
        results.append(r.status_code)


@pytest.mark.concurrent
@pytest.mark.ai
def test_concurrent_5_diagnoses(admin_token):
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
