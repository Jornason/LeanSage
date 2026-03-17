"""GENERATE: Empty description returns 422."""
import pytest


@pytest.mark.generate
def test_generate_empty_returns_422(client, admin_headers):
    r = client.post("/v1/generate/proof",
                    json={"description": ""},
                    headers=admin_headers)
    assert r.status_code == 422
