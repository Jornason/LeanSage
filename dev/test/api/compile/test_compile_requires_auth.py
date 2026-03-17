"""COMPILE: Compile without token returns 401 or 403."""
import pytest

VALID_CODE = "theorem foo : 1 + 1 = 2 := by norm_num"


@pytest.mark.compile
def test_compile_requires_auth(client):
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE})
    assert r.status_code in (401, 403)
