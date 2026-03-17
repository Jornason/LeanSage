"""GENERATE G01: Confidence should be > 0 (AI or fallback)."""
import pytest


@pytest.mark.generate
@pytest.mark.ai
def test_generate_confidence_threshold(client, admin_headers):
    """G01: Confidence should be > 0 (AI or fallback)."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove n + 0 = n for all natural numbers"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["confidence"] > 0
