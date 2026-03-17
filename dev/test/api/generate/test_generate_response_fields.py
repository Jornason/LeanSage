"""GENERATE: Response contains lean_code, confidence, and generation_time_ms."""
import pytest


@pytest.mark.generate
def test_generate_response_fields(client, admin_headers):
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove 1 + 1 = 2"},
                    headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "lean_code" in data
    assert "confidence" in data
    assert "generation_time_ms" in data
