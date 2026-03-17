"""EXPLAIN P08: Researcher plan can access detail_level=detailed."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_detailed_researcher(client, demo_headers):
    """P08: Researcher plan can access detail_level=detailed."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en",
                          "detail_level": "detailed"},
                    headers=demo_headers)
    assert r.status_code == 200
