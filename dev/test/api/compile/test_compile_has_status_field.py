"""COMPILE: Response data contains status field."""
import pytest

VALID_CODE = "theorem foo : 1 + 1 = 2 := by norm_num"


@pytest.mark.compile
def test_compile_has_status_field(client, admin_headers):
    r = client.post("/v1/compile/check",
                    json={"code": VALID_CODE},
                    headers=admin_headers)
    data = r.json()["data"]
    assert "status" in data
