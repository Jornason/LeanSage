"""EXPLAIN P04: language=zh is echoed back in response."""
import pytest

CODE_OMEGA = "theorem bar (n : Nat) : n + 1 > n :=\nby\n  omega"


@pytest.mark.explain
def test_explain_language_zh(client, admin_headers):
    """P04: language=zh is echoed back in response."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "zh"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["language"] == "zh"
