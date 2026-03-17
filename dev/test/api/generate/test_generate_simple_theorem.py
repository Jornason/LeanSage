"""GENERATE G01: Generate proof for 1+1=2, expect valid Lean 4 code."""
import pytest


@pytest.mark.generate
@pytest.mark.ai
def test_generate_simple_theorem(client, admin_headers):
    """G01: Generate proof for 1+1=2, expect valid Lean 4 code."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove that 1 + 1 = 2 for natural numbers"},
                    headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert len(data["lean_code"]) > 10
    assert any(kw in data["lean_code"] for kw in ("theorem", "lemma", "def"))
