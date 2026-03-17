"""GENERATE G-AUTH: Researcher plan can call generate."""
import pytest


@pytest.mark.generate
def test_generate_researcher_access(client, demo_headers):
    """G-AUTH: Researcher plan can call generate."""
    r = client.post("/v1/generate/proof",
                    json={"description": "Prove 1 + 1 = 2"},
                    headers=demo_headers)
    assert r.status_code == 200
