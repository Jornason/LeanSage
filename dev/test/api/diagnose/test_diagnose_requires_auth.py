"""DIAGNOSE: Diagnose without token returns 401 or 403."""
import pytest


@pytest.mark.diagnose
def test_diagnose_requires_auth(client):
    r = client.post("/v1/diagnose/error", json={
        "code": "theorem foo : True := trivial", "error_message": None,
    })
    assert r.status_code in (401, 403)
