"""DIAGNOSE D03: Unknown identifier suggests adding import."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_unknown_identifier(client, admin_headers):
    """D03: Unknown identifier suggests adding import."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : Continuous (fun x : ℝ => x) := by exact continuous_id",
        "error_message": "unknown identifier 'continuous_id'",
    }, headers=admin_headers)
    assert r.status_code == 200
    diags = r.json()["data"]["diagnostics"]
    assert len(diags) >= 1
    # Fix suggestion should mention import
    all_text = str(diags).lower()
    assert "import" in all_text or "mathlib" in all_text
