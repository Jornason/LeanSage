"""COMPILE: Lean code with sorry is compiled (mock accepts it)."""
import pytest


@pytest.mark.compile
def test_compile_sorry_code(client, admin_headers):
    """Lean code with sorry is compiled (mock accepts it)."""
    r = client.post("/v1/compile/check",
                    json={"code": "theorem foo : 1 = 2 := by sorry"},
                    headers=admin_headers)
    assert r.status_code == 200
