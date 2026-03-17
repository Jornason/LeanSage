"""SESSION-03: Retrieve a specific session by ID."""
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
def test_sessions_get_by_id(client, admin_headers, _session_id):
    """SESSION-03: Retrieve a specific session by ID."""
    r = client.get(f"/v1/proof/sessions/{_session_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["id"] == _session_id
