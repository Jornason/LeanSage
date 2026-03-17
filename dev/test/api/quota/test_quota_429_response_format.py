"""QUOTA: 429 response follows the standard API envelope."""
import pytest


@pytest.mark.quota
def test_quota_429_response_format(client, free_user):
    """429 response should follow the standard API envelope."""
    headers = free_user["headers"]
    for _ in range(15):
        r = client.post("/v1/search/mathlib",
                        json={"query": "limit test", "top_k": 1},
                        headers=headers)
        if r.status_code == 429:
            body = r.json()
            assert "detail" in body or "success" in body
            return
    pytest.skip("Did not trigger 429 within 15 requests")
