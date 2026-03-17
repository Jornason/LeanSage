"""
Error diagnosis tests.
Covers: D01-D06, D-FILTER
"""
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


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_unknown_tactic_has_suggestion(client, admin_headers):
    """D01: Diagnostic for unknown tactic includes at least one fix suggestion."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 1 := by\n  omega_bad",
        "error_message": "unknown tactic 'omega_bad'",
    }, headers=admin_headers)
    diags = r.json()["data"]["diagnostics"]
    assert len(diags[0]["suggestions"]) >= 1


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


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_unknown_identifier_suggests_import(client, admin_headers):
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


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_severity_filter_error_only(client, admin_headers):
    """D-FILTER: severity_filter=error excludes warnings."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 2 := by\n  sorry",
        "error_message": None,
        "severity_filter": "error",
    }, headers=admin_headers)
    assert r.status_code == 200
    diags = r.json()["data"]["diagnostics"]
    assert all(d["severity"] == "error" for d in diags)


@pytest.mark.diagnose
def test_diagnose_empty_code_returns_422(client, admin_headers):
    r = client.post("/v1/diagnose/error", json={
        "code": "", "error_message": None,
    }, headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.diagnose
def test_diagnose_requires_auth(client):
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : True := trivial", "error_message": None,
    })
    assert r.status_code in (401, 403)


@pytest.mark.diagnose
def test_diagnose_response_has_counts(client, admin_headers):
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 + 1 = 2 := by ring",
        "error_message": None,
    }, headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "total_errors" in data
    assert "total_warnings" in data
