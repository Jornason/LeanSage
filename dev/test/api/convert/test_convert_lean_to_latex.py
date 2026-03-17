"""CONVERT X02: Lean expression converts to a non-empty LaTeX string."""
import pytest

LEAN_FORALL = "∀ x : ℝ, x ^ 2 ≥ 0"


@pytest.mark.convert
def test_convert_lean_to_latex(client, admin_headers):
    """X02: Lean expression converts to a non-empty LaTeX string."""
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_FORALL},
                    headers=admin_headers)
    assert r.status_code == 200
    latex_out = r.json()["data"].get("latex", "")
    assert len(latex_out) > 3
