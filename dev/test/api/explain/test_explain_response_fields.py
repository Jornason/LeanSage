"""EXPLAIN: Response contains summary field."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_response_fields(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert "summary" in r.json()["data"]
