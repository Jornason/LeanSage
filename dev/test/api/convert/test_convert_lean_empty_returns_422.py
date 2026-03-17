"""CONVERT: Empty lean_code field is rejected with 422."""
import pytest


@pytest.mark.convert
def test_convert_lean_empty_returns_422(client, admin_headers):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": ""},
                    headers=admin_headers)
    assert r.status_code == 422
