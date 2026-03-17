"""GENERATE: Description longer than 2000 chars returns 422."""
import pytest


@pytest.mark.generate
def test_generate_overlong_returns_422(client, admin_headers):
    r = client.post("/v1/generate/proof",
                    json={"description": "x" * 2001},
                    headers=admin_headers)
    assert r.status_code == 422
