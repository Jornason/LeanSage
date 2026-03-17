"""CONVERT: latex-to-lean response has success=True."""
import pytest

LATEX_FORALL = r"\forall x : \mathbb{R}, x^2 \geq 0"


@pytest.mark.convert
def test_convert_success_flag(client, admin_headers):
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": LATEX_FORALL},
                    headers=admin_headers)
    assert r.json()["success"] is True
