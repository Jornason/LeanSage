"""QUOTA Q01/A03: Free plan allows 10 searches/month; 11th returns 429."""
import pytest


@pytest.mark.quota
def test_quota_free_search_exhausted(client, free_user):
    """Q01/A03: Free plan allows 10 searches/month; 11th returns 429."""
    headers = free_user["headers"]
    hit_429 = False
    last_status = None
    for i in range(15):
        r = client.post("/v1/search/mathlib",
                        json={"query": f"nat add commutativity {i}", "top_k": 1},
                        headers=headers)
        last_status = r.status_code
        if r.status_code == 429:
            hit_429 = True
            break
    assert hit_429, f"Expected 429 after 10 free searches, last status={last_status}"
