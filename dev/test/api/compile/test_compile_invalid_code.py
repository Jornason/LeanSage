"""COMPILE-02: Invalid Lean code returns 200 (endpoint always responds)."""
import pytest

INVALID_CODE = "theorem foo : 1 = 2 := by rfl"


@pytest.mark.compile
def test_compile_invalid_code(client, admin_headers):
    """COMPILE-02: Invalid Lean code returns 200 (endpoint always responds)."""
    r = client.post("/v1/compile/check",
                    json={"code": INVALID_CODE},
                    headers=admin_headers)
    assert r.status_code == 200
