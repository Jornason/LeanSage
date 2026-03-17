"""QUOTA Q02: Free plan cannot call proof generation."""
import pytest


@pytest.mark.quota
def test_quota_free_generate_blocked(client, free_user):
    """Q02: Free plan cannot call proof generation."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove 1 + 1 = 2"},
                    headers=free_user["headers"])
    assert r.status_code in (402, 403, 429)
