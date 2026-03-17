"""SESSION-06: Accessing a deleted session returns 404."""
import pytest


@pytest.mark.sessions
def test_sessions_404_after_delete(client, admin_headers):
    """SESSION-06: Accessing a deleted session returns 404."""
    r = client.post("/v1/proof/sessions", json={
        "title": "Gone", "description": "", "lean_code": "-- x",
    }, headers=admin_headers)
    sid = r.json()["data"]["id"]
    client.delete(f"/v1/proof/sessions/{sid}", headers=admin_headers)

    r_get = client.get(f"/v1/proof/sessions/{sid}", headers=admin_headers)
    assert r_get.status_code == 404
