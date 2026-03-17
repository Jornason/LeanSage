"""BILLING: Subscription response contains plan field."""
import pytest


@pytest.mark.billing
def test_billing_plan_field(client, admin_headers):
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    data = r.json()["data"]
    assert "plan" in data
