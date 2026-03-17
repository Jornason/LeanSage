"""
LaTeX ↔ Lean conversion tests.
Covers: X01, X02, X05, X09, X10
"""
import pytest

LATEX_FORALL  = r"\forall x : \mathbb{R}, x^2 \geq 0"
LEAN_FORALL   = "∀ x : ℝ, x ^ 2 ≥ 0"
LEAN_UNICODE  = "∀ x, ∃ y, x ∈ Set.univ ∧ y ∉ ∅"


@pytest.mark.convert
def test_latex_to_lean_basic(client, admin_headers):
    """X01: LaTeX expression converts to a non-empty Lean expression."""
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": LATEX_FORALL},
                    headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    result = data.get("lean_expression") or data.get("lean_declaration") or data.get("lean_code", "")
    assert len(result) > 3


@pytest.mark.convert
def test_lean_to_latex_basic(client, admin_headers):
    """X02: Lean expression converts to a non-empty LaTeX string."""
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_FORALL},
                    headers=admin_headers)
    assert r.status_code == 200
    latex_out = r.json()["data"].get("latex", "")
    assert len(latex_out) > 3


@pytest.mark.convert
def test_latex_to_lean_empty_returns_422(client, admin_headers):
    """X05: Empty latex field is rejected."""
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": ""},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.convert
def test_lean_to_latex_empty_returns_422(client, admin_headers):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": ""},
                    headers=admin_headers)
    assert r.status_code == 422


@pytest.mark.convert
def test_roundtrip_latex_lean_latex(client, admin_headers):
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


@pytest.mark.convert
def test_lean_to_latex_unicode_symbols(client, admin_headers):
    """X10: Lean code with ∀∃∈∉ converts without error."""
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_UNICODE},
                    headers=admin_headers)
    assert r.status_code == 200
    latex_out = r.json()["data"].get("latex", "")
    assert len(latex_out) > 3


@pytest.mark.convert
def test_convert_requires_auth(client):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_FORALL})
    assert r.status_code in (401, 403)


@pytest.mark.convert
def test_latex_to_lean_returns_success(client, admin_headers):
    r = client.post("/v1/convert/latex-to-lean",
                    json={"latex": LATEX_FORALL},
                    headers=admin_headers)
    assert r.json()["success"] is True
