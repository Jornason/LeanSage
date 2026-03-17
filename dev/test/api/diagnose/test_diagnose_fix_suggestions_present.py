"""DIAGNOSE D01: Diagnostic for unknown tactic includes at least one fix suggestion."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_fix_suggestions_present(client, admin_headers):
    """D01: Diagnostic for unknown tactic includes at least one fix suggestion."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 1 := by\n  omega_bad",
        "error_message": "unknown tactic 'omega_bad'",
    }, headers=admin_headers)
    diags = r.json()["data"]["diagnostics"]
    assert len(diags[0]["suggestions"]) >= 1
