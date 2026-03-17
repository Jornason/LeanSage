"""EXPLAIN P06: Unknown tactic (trivial) falls back to AI for explanation."""
import pytest

CODE_TRIVIAL = "theorem baz : True :=\nby\n  trivial"


@pytest.mark.explain
@pytest.mark.ai
def test_explain_unknown_tactic_ai(client, admin_headers):
    """P06: Unknown tactic (trivial) falls back to AI for explanation."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_TRIVIAL, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    trivial = next((s for s in steps if s["tactic"] == "trivial"), None)
    assert trivial is not None, f"trivial not found in steps: {[s['tactic'] for s in steps]}"
    assert len(trivial["explanation"]) > 10
