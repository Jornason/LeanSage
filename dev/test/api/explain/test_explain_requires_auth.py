"""EXPLAIN: Explain without token returns 401 or 403."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_requires_auth(client):
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"})
    assert r.status_code in (401, 403)
