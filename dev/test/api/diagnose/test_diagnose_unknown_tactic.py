"""DIAGNOSE D01: Unknown tactic returns diagnostic with fix suggestion."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_unknown_tactic(client, admin_headers):
    """D01: Unknown tactic returns diagnostic with fix suggestion."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 1 := by\n  omega_bad",
        "error_message": "unknown tactic 'omega_bad'",
    }, headers=admin_headers)
    assert r.status_code == 200
    diags = r.json()["data"]["diagnostics"]
    assert len(diags) >= 1
