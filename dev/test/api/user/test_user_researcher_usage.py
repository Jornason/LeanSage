"""USER Q03: Researcher plan user can retrieve usage."""
import pytest


@pytest.mark.user
def test_user_researcher_usage(client, demo_headers):
    """Q03: Researcher plan user can retrieve usage."""
    r = client.get("/v1/user/usage", headers=demo_headers)
    assert r.status_code == 200
