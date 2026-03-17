"""DIAGNOSE D-FILTER: severity_filter=error excludes warnings."""
import pytest


@pytest.mark.diagnose
@pytest.mark.ai
def test_diagnose_severity_filter(client, admin_headers):
    """D-FILTER: severity_filter=error excludes warnings."""
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : 1 = 2 := by\n  sorry",
        "error_message": None,
        "severity_filter": "error",
    }, headers=admin_headers)
    assert r.status_code == 200
    diags = r.json()["data"]["diagnostics"]
    assert all(d["severity"] == "error" for d in diags)
