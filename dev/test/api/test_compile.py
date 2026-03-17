"""
Lean compilation check tests.
Covers: COMPILE-01 to COMPILE-03
"""
import pytest

VALID_CODE   = "theorem foo : 1 + 1 = 2 := by norm_num"
INVALID_CODE = "theorem foo : 1 = 2 := by rfl"


@pytest.mark.compile
def test_compile_valid_code(client, admin_headers):
    """COMPILE-01: Well-formed Lean code returns 200."""
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


@pytest.mark.compile
def test_compile_invalid_code(client, admin_headers):
    """COMPILE-02: Invalid Lean code returns 200 (endpoint always responds)."""
    r = client.post("/v1/compile/check",
                    json={"code": INVALID_CODE},
                    headers=admin_headers)
    assert r.status_code == 200


@pytest.mark.compile
def test_compile_empty_code_returns_422(client, admin_headers):
    """COMPILE-03: Empty code field is rejected at schema level."""
    r = client.post("/v1/compile/check",
                    json={"code": ""},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.compile
def test_compile_response_has_status(client, admin_headers):
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE},
                    headers=admin_headers)
    data = r.json()["data"]
    assert "status" in data


@pytest.mark.compile
def test_compile_requires_auth(client):
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE})
    assert r.status_code in (401, 403)


@pytest.mark.compile
def test_compile_code_with_sorry(client, admin_headers):
    """Lean code with sorry is compiled (mock accepts it)."""
    r = client.post("/v1/compile/check",
                    json={"code": "theorem foo : 1 = 2 := by sorry"},
                    headers=admin_headers)
    assert r.status_code == 200
