"""COMPILE-03: Empty code field is rejected at schema level with 422."""
import pytest


@pytest.mark.compile
def test_compile_empty_returns_422(client, admin_headers):
    """COMPILE-03: Empty code field is rejected at schema level."""
    r = client.post("/v1/compile/check",
                    json={"code": ""},
                    headers=admin_headers)
    assert r.status_code == 422
