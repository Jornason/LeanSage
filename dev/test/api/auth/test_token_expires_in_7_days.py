"""AUTH: Token expires_in is approximately 7 days."""
import pytest


@pytest.mark.auth
def test_token_expires_in_7_days(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    expires_in = r.json()["data"].get("expires_in", 0)
    # 7 days = 604800 seconds (allow ±60s)
    assert abs(expires_in - 604800) < 60 or expires_in == 10080  # minutes variant
