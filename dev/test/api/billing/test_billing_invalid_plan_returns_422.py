"""BILLING: Invalid plan name is rejected with 422."""
import pytest


@pytest.mark.billing
def test_billing_invalid_plan_returns_422(client, demo_headers):
    """Invalid plan name is rejected with 422."""
    r = client.post("/v1/billing/create-checkout",
                    json={"plan": "invalid_plan", "billing_cycle": "monthly"},
                    headers=demo_headers)
    assert r.status_code == 422
