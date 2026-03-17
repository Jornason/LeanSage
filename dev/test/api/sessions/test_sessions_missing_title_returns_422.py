"""SESSION: Creating a session without title returns 422."""
import pytest


@pytest.mark.sessions
def test_sessions_missing_title_returns_422(client, admin_headers):
    r = client.post("/v1/proof/sessions",
                    json={"lean_code": "-- test"},
                    headers=admin_headers)
    assert r.status_code == 422
