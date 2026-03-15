"""
User Router
GET /v1/user/usage
GET /v1/user/profile
"""

from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import Literal

from app.schemas.api import UsageResponse, UsageStats
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan, get_quota_usage,
    PLAN_MONTHLY_LIMITS, PLAN_RATE_LIMITS, check_rate_limit,
)

router = APIRouter()

# Mock usage data
MOCK_USAGE = {
    "user_demo_123": {
        "plan": "researcher",
        "searches": 47,
        "generations": 12,
        "diagnoses": 8,
        "compilations": 23,
        "api_calls_today": 15,
    },
    "user_admin_001": {
        "plan": "admin",
        "searches": 0,
        "generations": 0,
        "diagnoses": 0,
        "compilations": 0,
        "api_calls_today": 0,
    },
}


@router.get("/user/usage")
async def get_usage(
    period: Literal["current_month", "last_month", "all"] = "current_month",
    user_id: str = Depends(get_current_user_id),
):
    """Get current user's API usage statistics. Requires authentication."""
    user_plan = get_user_plan(user_id)
    quota = get_quota_usage(user_id, user_plan)
    monthly_limit = PLAN_MONTHLY_LIMITS.get(user_plan, 10)
    rate_limit_rpm = PLAN_RATE_LIMITS.get(user_plan, 10)
    rate_info = check_rate_limit(user_id, user_plan)

    usage = MOCK_USAGE.get(user_id, {
        "plan": user_plan,
        "searches": 0,
        "generations": 0,
        "diagnoses": 0,
        "compilations": 0,
        "api_calls_today": 0,
    })

    year_month = datetime.utcnow().strftime("%Y-%m")

    response = UsageResponse(
        plan=user_plan,
        period=year_month,
        searches=UsageStats(used=usage["searches"], limit=monthly_limit),
        generations=UsageStats(used=usage["generations"], limit=monthly_limit),
        diagnoses=UsageStats(used=usage["diagnoses"], limit=monthly_limit),
        compilations=UsageStats(used=usage["compilations"], limit=monthly_limit),
        api_calls_today=usage["api_calls_today"],
        rate_limit={
            "requests_per_minute": rate_limit_rpm,
            "remaining": rate_info["remaining"],
        },
    )
    return ok(response.model_dump())


@router.get("/user/profile")
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """Get current user's profile. Requires authentication."""
    from app.routers.auth import MOCK_USERS

    # Look up user from mock store
    for user_data in MOCK_USERS.values():
        if user_data.get("id") == user_id:
            return ok({
                "id": user_id,
                "email": user_data["email"],
                "display_name": user_data["display_name"],
                "role": user_data.get("role", "free"),
                "avatar_url": user_data.get("avatar_url"),
                "locale": user_data.get("locale", "en"),
                "usage_count_month": 0,
                "created_at": user_data.get("created_at", ""),
            })

    # Fallback for unknown users
    user_plan = get_user_plan(user_id)
    return ok({
        "id": user_id,
        "email": "unknown@leanprove.ai",
        "display_name": "Unknown User",
        "role": user_plan,
        "avatar_url": None,
        "locale": "en",
        "usage_count_month": 0,
        "created_at": "",
    })
