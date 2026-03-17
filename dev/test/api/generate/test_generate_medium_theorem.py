"""GENERATE G02: Medium complexity theorem returns non-empty Lean code."""
import pytest


@pytest.mark.generate
@pytest.mark.ai
def test_generate_medium_theorem(client, admin_headers):
    """G02: Medium complexity theorem returns non-empty Lean code."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove n + 0 = n by induction on n"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["lean_code"]) > 10
