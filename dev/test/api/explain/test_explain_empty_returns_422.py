"""EXPLAIN: Empty code returns 422."""
import pytest


@pytest.mark.explain
def test_explain_empty_returns_422(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": "", "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 422
