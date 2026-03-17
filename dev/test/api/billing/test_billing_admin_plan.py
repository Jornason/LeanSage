"""BILLING: Admin subscription plan is 'admin'."""
import pytest


@pytest.mark.billing
def test_billing_admin_plan(client, admin_headers):
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    assert r.json()["data"]["plan"] == "admin"
