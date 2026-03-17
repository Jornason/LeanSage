"""EXPLAIN P01/P02: ring tactic is explained from dictionary."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_tactic_ring(client, admin_headers):
    """P01/P02: Known tactics (ring, simp) are explained from dictionary."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    names = [s["tactic"] for s in steps]
    assert any(t in names for t in ("ring", "simp"))
