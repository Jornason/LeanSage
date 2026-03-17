"""DIAGNOSE: Empty code returns 422."""
import pytest


@pytest.mark.diagnose
def test_diagnose_empty_returns_422(client, admin_headers):
    r = client.post("/v1/diagnose/error", json={
        "code": "", "error_message": None,
    }, headers=admin_headers)
    assert r.status_code == 422
