"""Smoke: lean-to-latex conversion returns 200."""
import pytest


@pytest.mark.smoke
def test_lean_to_latex(client, admin_headers):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": "∀ x : ℝ, x ≥ 0"},
                    headers=admin_headers)
    assert r.status_code == 200
