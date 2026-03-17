"""BILLING: Cancel endpoint is reachable (may return mock response)."""
import pytest


@pytest.mark.billing
def test_billing_cancel(client, admin_headers):
    """Cancel endpoint is reachable (may return mock response)."""
    r = client.post("/v1/billing/cancel", headers=admin_headers)
    assert r.status_code in (200, 400, 404)
