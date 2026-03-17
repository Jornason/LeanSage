"""SESSION: Sessions endpoint without token returns 401 or 403."""
import pytest


@pytest.mark.sessions
def test_sessions_requires_auth(client):
    r = client.get("/v1/proof/sessions")
    assert r.status_code in (401, 403)
