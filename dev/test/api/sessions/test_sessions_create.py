"""SESSION-01: Create a new proof session."""
import pytest


@pytest.mark.sessions
def test_sessions_create(client, admin_headers):
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
