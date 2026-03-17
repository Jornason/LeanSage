"""GENERATE I: Chinese description is accepted."""
import pytest


@pytest.mark.generate
@pytest.mark.ai
def test_generate_chinese_description(client, admin_headers):
    """I: Chinese description is accepted."""
    r = client.post("/v1/generate/proof",
                    json={"description": "证明自然数 n 满足 n + 0 = n"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
