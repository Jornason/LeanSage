"""CONVERT X09: LaTeX → Lean → LaTeX round-trip returns non-empty LaTeX."""
import pytest


@pytest.mark.convert
def test_convert_round_trip(client, admin_headers):
    """X09: LaTeX → Lean → LaTeX round-trip returns non-empty LaTeX."""
    r1 = client.post("/v1/convert/latex-to-lean",
                     json={"latex": r"\forall n : \mathbb{N}, n + 0 = n"},
                     headers=admin_headers)
    assert r1.status_code == 200
    data1 = r1.json()["data"]
    lean_mid = data1.get("lean_expression") or data1.get("lean_declaration") or data1.get("lean_code", "")
    assert len(lean_mid) > 3

    r2 = client.post("/v1/convert/lean-to-latex",
                     json={"lean_code": lean_mid},
                     headers=admin_headers)
    assert r2.status_code == 200
    latex_rt = r2.json()["data"].get("latex", "")
    assert len(latex_rt) > 3
