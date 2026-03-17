"""CONVERT X05: Empty latex field is rejected with 422."""
import pytest


@pytest.mark.convert
def test_convert_latex_empty_returns_422(client, admin_headers):
    """X05: Empty latex field is rejected."""
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": ""},
                    headers=admin_headers)
    assert r.status_code == 422
