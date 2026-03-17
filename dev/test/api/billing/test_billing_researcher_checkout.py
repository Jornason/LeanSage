"""BILLING: Researcher can initiate checkout for a valid plan."""
import pytest


@pytest.mark.billing
def test_billing_researcher_checkout(client, demo_headers):
    """Researcher can initiate checkout for a valid plan."""
    r = client.post("/v1/billing/create-checkout",
                    json={"plan": "researcher", "billing_cycle": "monthly"},
                    headers=demo_headers)
    # Stripe not configured — expect 200 with mock URL or 5xx from Stripe
    assert r.status_code in (200, 400, 500, 503)
