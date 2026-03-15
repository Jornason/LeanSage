"""
Billing / Subscription Router
GET  /v1/billing/subscription
POST /v1/billing/create-checkout
POST /v1/billing/webhook  (Stripe webhook)
POST /v1/billing/cancel
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request

from app.schemas.api import CreateCheckoutRequest, SubscriptionResponse
from app.schemas.common import ok
from app.core.auth import get_current_user_id, get_user_plan, check_rate_limit

router = APIRouter()

# Mock subscription data
MOCK_SUBSCRIPTIONS: dict[str, dict] = {
    "user_demo_123": {
        "id": "sub_demo_1",
        "user_id": "user_demo_123",
        "plan": "researcher",
        "status": "active",
        "stripe_customer_id": "cus_mock_123",
        "stripe_subscription_id": "sub_mock_123",
        "current_period_start": "2026-03-01T00:00:00Z",
        "current_period_end": "2026-04-01T00:00:00Z",
        "cancel_at_period_end": False,
        "created_at": "2026-01-15T00:00:00Z",
        "updated_at": "2026-03-01T00:00:00Z",
    },
    "user_admin_001": {
        "id": "sub_admin_1",
        "user_id": "user_admin_001",
        "plan": "admin",
        "status": "active",
        "stripe_customer_id": "cus_admin_001",
        "stripe_subscription_id": "sub_admin_001",
        "current_period_start": "2026-01-01T00:00:00Z",
        "current_period_end": "2099-12-31T00:00:00Z",
        "cancel_at_period_end": False,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    },
}

PLAN_PRICES = {
    "researcher": {"monthly": 1900, "annual": 18240, "stripe_price_id": "price_researcher_monthly"},
    "lab": {"monthly": 9900, "annual": 95040, "stripe_price_id": "price_lab_monthly"},
    "enterprise": {"monthly": 29900, "annual": 287040, "stripe_price_id": "price_enterprise_monthly"},
}


@router.get("/billing/subscription")
async def get_subscription(
    user_id: str = Depends(get_current_user_id),
):
    """Get the current user's subscription details. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    subscription = MOCK_SUBSCRIPTIONS.get(user_id)

    if not subscription:
        return ok(SubscriptionResponse(
            plan="free",
            status="active",
            current_period_start=None,
            current_period_end=None,
            cancel_at_period_end=False,
        ).model_dump())

    return ok(SubscriptionResponse(
        plan=subscription["plan"],
        status=subscription["status"],
        current_period_start=subscription.get("current_period_start"),
        current_period_end=subscription.get("current_period_end"),
        cancel_at_period_end=subscription.get("cancel_at_period_end", False),
    ).model_dump())


@router.post("/billing/create-checkout")
async def create_checkout_session(
    request: CreateCheckoutRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Create a Stripe Checkout session for subscription upgrade.
    In production, calls Stripe API to generate a checkout URL.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    if request.plan not in PLAN_PRICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {request.plan}. Must be one of: {list(PLAN_PRICES.keys())}",
        )

    price_info = PLAN_PRICES[request.plan]
    amount = price_info["monthly"] if request.billing_cycle == "monthly" else price_info["annual"]

    # Mock: In production, create Stripe checkout session
    return ok({
        "checkout_url": f"https://checkout.stripe.com/mock?plan={request.plan}&cycle={request.billing_cycle}",
        "session_id": "cs_mock_session_123",
        "plan": request.plan,
        "billing_cycle": request.billing_cycle,
        "amount": amount,
        "currency": "usd",
    })


@router.post("/billing/webhook")
async def stripe_webhook(request: Request):
    """
    Handle Stripe webhook events (subscription created/updated/canceled).
    In production, verify webhook signature and process events.
    No authentication required (Stripe calls this endpoint directly).
    """
    body = await request.body()

    # Mock: In production, verify Stripe signature and process event
    # stripe.Webhook.construct_event(body, sig_header, webhook_secret)

    return ok({"received": True})


@router.post("/billing/cancel")
async def cancel_subscription(
    user_id: str = Depends(get_current_user_id),
):
    """Cancel the current subscription at the end of the billing period. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    subscription = MOCK_SUBSCRIPTIONS.get(user_id)

    if not subscription or subscription["plan"] == "free":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active paid subscription to cancel",
        )

    subscription["status"] = "canceled"
    subscription["cancel_at_period_end"] = True
    subscription["updated_at"] = datetime.utcnow().isoformat() + "Z"

    return ok({
        "message": "Subscription will be canceled at the end of the current billing period",
        "cancel_at": subscription["current_period_end"],
        "plan": subscription["plan"],
    })
