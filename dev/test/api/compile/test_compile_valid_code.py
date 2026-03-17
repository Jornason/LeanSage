"""COMPILE-01: Well-formed Lean code returns 200."""
import pytest

VALID_CODE = "theorem foo : 1 + 1 = 2 := by norm_num"


@pytest.mark.compile
def test_compile_valid_code(client, admin_headers):
    """COMPILE-01: Well-formed Lean code returns 200."""
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
