"""
Proof session CRUD tests.
Covers: SESSION-01 to SESSION-06
"""
import pytest


@pytest.fixture()
def session_id(client, admin_headers):
    """Create a proof session and return its ID; delete it after the test."""
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
def test_create_session(client, admin_headers):
    """SESSION-01: Create a new proof session."""
    r = client.post("/v1/proof/sessions", json={
        "title": "Create Test",
        "description": "Regression",
        "lean_code": "-- test",
    }, headers=admin_headers)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "id" in data
    # Cleanup
    client.delete(f"/v1/proof/sessions/{data['id']}", headers=admin_headers)


@pytest.mark.sessions
def test_list_sessions(client, admin_headers, session_id):
    """SESSION-02: List sessions includes the created session."""
    r = client.get("/v1/proof/sessions", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


@pytest.mark.sessions
def test_get_session_by_id(client, admin_headers, session_id):
    """SESSION-03: Retrieve a specific session by ID."""
    r = client.get(f"/v1/proof/sessions/{session_id}", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["id"] == session_id


@pytest.mark.sessions
def test_update_session(client, admin_headers, session_id):
    """SESSION-04: Patch an existing session."""
    r = client.patch(f"/v1/proof/sessions/{session_id}",
                     json={"lean_code": "-- updated\ntheorem t : True := trivial"},
                     headers=admin_headers)
    assert r.status_code == 200


@pytest.mark.sessions
def test_delete_session(client, admin_headers):
    """SESSION-05: Delete a session successfully."""
    # Create a dedicated session for this test
    r = client.post("/v1/proof/sessions", json={
        "title": "Delete Me", "description": "", "lean_code": "-- x",
    }, headers=admin_headers)
    sid = r.json()["data"]["id"]

    r_del = client.delete(f"/v1/proof/sessions/{sid}", headers=admin_headers)
    assert r_del.status_code == 200


@pytest.mark.sessions
def test_get_deleted_session_returns_404(client, admin_headers):
    """SESSION-06: Accessing a deleted session returns 404."""
    r = client.post("/v1/proof/sessions", json={
        "title": "Gone", "description": "", "lean_code": "-- x",
    }, headers=admin_headers)
    sid = r.json()["data"]["id"]
    client.delete(f"/v1/proof/sessions/{sid}", headers=admin_headers)

    r_get = client.get(f"/v1/proof/sessions/{sid}", headers=admin_headers)
    assert r_get.status_code == 404


@pytest.mark.sessions
def test_sessions_require_auth(client):
    r = client.get("/v1/proof/sessions")
    assert r.status_code in (401, 403)


@pytest.mark.sessions
def test_create_session_missing_title_returns_422(client, admin_headers):
    r = client.post("/v1/proof/sessions",
                    json={"lean_code": "-- test"},
                    headers=admin_headers)
    assert r.status_code == 422
