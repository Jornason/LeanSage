"""CONVERT X10: Lean code with Unicode symbols converts without error."""
import pytest

LEAN_UNICODE = "∀ x, ∃ y, x ∈ Set.univ ∧ y ∉ ∅"


@pytest.mark.convert
def test_convert_unicode(client, admin_headers):
    """X10: Lean code with ∀∃∈∉ converts without error."""
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": LEAN_UNICODE},
                    headers=admin_headers)
    assert r.status_code == 200
    latex_out = r.json()["data"].get("latex", "")
    assert len(latex_out) > 3
