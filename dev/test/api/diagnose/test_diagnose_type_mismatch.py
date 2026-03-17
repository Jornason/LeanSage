"""DIAGNOSE D02: Type mismatch error is diagnosed."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_type_mismatch(client, admin_headers):
    """D02: Type mismatch error is diagnosed."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo (n : Nat) : n = (n : Int) := by rfl",
        "error_message": "type mismatch",
    }, headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["diagnostics"]) >= 1
