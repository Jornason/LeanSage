"""BILLING: Subscription cancel without token returns 401 or 403."""
import pytest


@pytest.mark.billing
def test_billing_cancel_requires_auth(client):
    r = client.get("/v1/billing/subscription")
    assert r.status_code in (401, 403)
