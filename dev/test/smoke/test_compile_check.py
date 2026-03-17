"""Smoke: compile check endpoint returns 200 for valid Lean code."""
import pytest


@pytest.mark.smoke
def test_compile_check(client, admin_headers):
    r = client.post("/v1/compile/check",
                    json={"code": "theorem t : True := trivial"},
                    headers=admin_headers)
    assert r.status_code == 200
