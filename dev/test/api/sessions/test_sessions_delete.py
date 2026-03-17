"""SESSION-05: Delete a session successfully."""
import pytest


@pytest.mark.sessions
def test_sessions_delete(client, admin_headers):
    """SESSION-05: Delete a session successfully."""
    # Create a dedicated session for this test
    r = client.post("/v1/proof/sessions", json={
        "title": "Delete Me", "description": "", "lean_code": "-- x",
    }, headers=admin_headers)
    sid = r.json()["data"]["id"]

    r_del = client.delete(f"/v1/proof/sessions/{sid}", headers=admin_headers)
    assert r_del.status_code == 200
