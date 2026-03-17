"""CONVERT: Convert without token returns 401 or 403."""
import pytest

LEAN_FORALL = "∀ x : ℝ, x ^ 2 ≥ 0"


@pytest.mark.convert
def test_convert_requires_auth(client):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_FORALL})
    assert r.status_code in (401, 403)
