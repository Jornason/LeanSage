"""Smoke: explain known tactic returns 200 success."""
import pytest


@pytest.mark.smoke
def test_explain_known_tactic(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": "theorem f :=\nby\n  ring", "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
