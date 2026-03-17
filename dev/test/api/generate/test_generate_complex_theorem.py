"""GENERATE G03: Complex theorem generates a proof scaffold (may contain sorry)."""
import pytest


@pytest.mark.generate
@pytest.mark.ai
@pytest.mark.slow
def test_generate_complex_theorem(client, admin_headers):
    """G03: Complex theorem generates a proof scaffold (may contain sorry)."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove the intermediate value theorem"},
                    headers=admin_headers, timeout=90)
    assert r.status_code == 200
    assert len(r.json()["data"]["lean_code"]) > 10
