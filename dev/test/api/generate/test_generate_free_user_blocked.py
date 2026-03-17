"""GENERATE Q02: Free plan cannot access proof generation."""
import pytest


@pytest.mark.generate
def test_generate_free_user_blocked(client, free_user):
    """Q02: Free plan cannot access proof generation."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove 1 + 1 = 2"},
                    headers=free_user["headers"])
    assert r.status_code in (402, 403, 429)
