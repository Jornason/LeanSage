"""DIAGNOSE: Response contains total_errors and total_warnings fields."""
import pytest


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
