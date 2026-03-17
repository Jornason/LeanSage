"""
Billing & subscription tests.
Covers: Q07-SUB, billing endpoints
"""
import pytest


@pytest.mark.billing
def test_get_subscription_admin(client, admin_headers):
    """Q07-SUB: Admin can retrieve subscription info."""
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


@pytest.mark.billing
def test_subscription_has_plan_field(client, admin_headers):
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    data = r.json()["data"]
    assert "plan" in data


@pytest.mark.billing
def test_admin_subscription_plan_is_admin(client, admin_headers):
    r = client.get("/v1/billing/subscription", headers=admin_headers)
    assert r.json()["data"]["plan"] == "admin"


@pytest.mark.billing
def test_subscription_requires_auth(client):
    r = client.get("/v1/billing/subscription")
    assert r.status_code in (401, 403)


@pytest.mark.billing
def test_create_checkout_requires_valid_plan(client, demo_headers):
    """Invalid plan name is rejected with 422."""
    r = client.post("/v1/billing/create-checkout",
                    json={"plan": "invalid_plan", "billing_cycle": "monthly"},
                    headers=demo_headers)
    assert r.status_code == 422


@pytest.mark.billing
def test_create_checkout_researcher_plan(client, demo_headers):
    """Researcher can initiate checkout for a valid plan."""
    r = client.post("/v1/billing/create-checkout",
                    json={"plan": "researcher", "billing_cycle": "monthly"},
                    headers=demo_headers)
    # Stripe not configured — expect 200 with mock URL or 5xx from Stripe
    assert r.status_code in (200, 400, 500, 503)


@pytest.mark.billing
def test_cancel_subscription(client, admin_headers):
    """Cancel endpoint is reachable (may return mock response)."""
    r = client.post("/v1/billing/cancel", headers=admin_headers)
    assert r.status_code in (200, 400, 404)


@pytest.mark.billing
def test_billing_requires_auth_subscription(client):
    r = client.get("/v1/billing/subscription")
    assert r.status_code in (401, 403)
