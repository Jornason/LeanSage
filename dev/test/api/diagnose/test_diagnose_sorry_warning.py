"""DIAGNOSE D05b: Code containing sorry triggers a warning."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_sorry_warning(client, admin_headers):
    """D05b: Code containing sorry triggers a warning."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 2 := by\n  sorry",
        "error_message": None,
    }, headers=admin_headers)
    assert r.status_code == 200
    diags = r.json()["data"]["diagnostics"]
    has_warning = any(
        d.get("severity") == "warning" or "sorry" in d.get("explanation", "").lower()
        for d in diags
    )
    assert has_warning, f"No sorry warning found in: {diags}"
