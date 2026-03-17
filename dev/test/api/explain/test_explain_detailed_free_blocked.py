"""EXPLAIN P08: Free plan cannot access detailed explanations."""
import pytest

CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"


@pytest.mark.explain
def test_explain_detailed_free_blocked(client, free_user):
    """P08: Free plan cannot access detailed explanations."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en",
                          "detail_level": "detailed"},
                    headers=free_user["headers"])
    assert r.status_code in (402, 403, 429)
