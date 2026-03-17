"""BILLING Q07-SUB: Admin can retrieve subscription info."""
import pytest


@pytest.mark.billing
def test_billing_get_subscription(client, admin_headers):
    """Q07-SUB: Admin can retrieve subscription info."""
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True
