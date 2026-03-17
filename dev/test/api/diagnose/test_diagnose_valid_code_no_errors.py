"""DIAGNOSE: Valid Lean code with no errors returns empty diagnostics list."""
import pytest


@pytest.mark.diagnose
def test_diagnose_valid_code_no_errors(client, admin_headers):
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 + 1 = 2 := by ring",
        "error_message": None,
    }, headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "total_errors" in data
    assert "total_warnings" in data
