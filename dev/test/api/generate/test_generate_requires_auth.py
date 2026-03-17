"""GENERATE: Generate without token returns 401 or 403."""
import pytest


@pytest.mark.generate
def test_generate_requires_auth(client):
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove 1 + 1 = 2"})
    assert r.status_code in (401, 403)
