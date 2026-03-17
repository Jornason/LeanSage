"""EXPLAIN P03: omega tactic explanation is non-empty."""
import pytest

CODE_OMEGA = "theorem bar (n : Nat) : n + 1 > n :=\nby\n  omega"


@pytest.mark.explain
def test_explain_tactic_omega(client, admin_headers):
    """P03: omega tactic explanation is non-empty."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    omega_step = next((s for s in steps if s["tactic"] == "omega"), None)
    assert omega_step is not None
    assert len(omega_step["explanation"]) > 10
