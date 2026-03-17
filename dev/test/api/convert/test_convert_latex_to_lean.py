"""CONVERT X01: LaTeX expression converts to a non-empty Lean expression."""
import pytest

LATEX_FORALL = r"\forall x : \mathbb{R}, x^2 \geq 0"


@pytest.mark.convert
def test_convert_latex_to_lean(client, admin_headers):
    """X01: LaTeX expression converts to a non-empty Lean expression."""
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": LATEX_FORALL},
                    headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    result = data.get("lean_expression") or data.get("lean_declaration") or data.get("lean_code", "")
    assert len(result) > 3
