"""EXPLAIN P05: language=en is echoed back in response."""
import pytest

CODE_OMEGA = "theorem bar (n : Nat) : n + 1 > n :=\nby\n  omega"


@pytest.mark.explain
def test_explain_language_en(client, admin_headers):
    """P05: language=en is echoed back in response."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["language"] == "en"
