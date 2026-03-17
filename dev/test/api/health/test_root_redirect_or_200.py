"""HEALTH-05: Root path returns 200."""
import pytest


@pytest.mark.smoke
def test_root_redirect_or_200(client):
    r = client.get("/")
    assert r.status_code == 200
