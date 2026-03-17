"""SESSION-04: Patch an existing session."""
import pytest


@pytest.fixture()
def _session_id(client, admin_headers):
    r = client.post("/v1/proof/sessions", json={
        "title": "Pytest Session",
        "description": "Created by regression test",
        "lean_code": "theorem test : 1 + 1 = 2 := by norm_num",
    }, headers=admin_headers)
    assert r.status_code == 200
    sid = r.json()["data"]["id"]
    yield sid
    client.delete(f"/v1/proof/sessions/{sid}", headers=admin_headers)


@pytest.mark.sessions
def test_sessions_update(client, admin_headers, _session_id):
    """SESSION-04: Patch an existing session."""
    r = client.patch(f"/v1/proof/sessions/{_session_id}",
                     json={"lean_code": "-- updated\ntheorem t : True := trivial"},
                     headers=admin_headers)
    assert r.status_code == 200
