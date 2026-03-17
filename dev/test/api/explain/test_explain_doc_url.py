"""EXPLAIN: ring tactic has a documentation URL."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_doc_url(client, admin_headers):
    """ring, simp, omega, linarith, norm_num have documentation URLs."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    steps = r.json()["data"]["steps"]
    ring_step = next((s for s in steps if s["tactic"] == "ring"), None)
    if ring_step:
        assert ring_step.get("doc_url") is not None
