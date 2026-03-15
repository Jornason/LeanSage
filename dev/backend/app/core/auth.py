"""
JWT Authentication utilities, role-based access control, quota enforcement, and rate limiting.
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.config import settings

security = HTTPBearer(auto_error=False)
security_required = HTTPBearer(auto_error=True)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security_required),
) -> str:
    """Required authentication - raises 401 if no valid token."""
    payload = decode_token(credentials.credentials)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return user_id


async def get_optional_user_id(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[str]:
    """Optional authentication - returns None if no token provided."""
    if credentials is None:
        return None
    try:
        payload = decode_token(credentials.credentials)
        return payload.get("sub")
    except HTTPException:
        return None


# ---------------------------------------------------------------------------
# Plan / Role-Based Access Control
# ---------------------------------------------------------------------------

PLAN_HIERARCHY = ["free", "researcher", "lab", "admin"]


def require_plan(user_plan: str, allowed_plans: list[str]) -> None:
    """
    Raise 403 if the user's plan is not in the allowed list.
    Call this at the top of any endpoint that requires a specific tier.
    """
    if user_plan not in allowed_plans:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"This feature requires one of the following plans: {', '.join(allowed_plans)}. "
                   f"Your current plan is '{user_plan}'.",
        )


# ---------------------------------------------------------------------------
# Quota Enforcement
# ---------------------------------------------------------------------------

# Monthly query limits per plan
PLAN_MONTHLY_LIMITS: dict[str, int] = {
    "free": 10,
    "researcher": -1,  # unlimited
    "lab": 500,
    "admin": -1,  # unlimited
}

# In-memory usage tracker: user_id -> {"month": "YYYY-MM", "count": int}
_usage_tracker: dict[str, dict] = defaultdict(lambda: {"month": "", "count": 0})


def check_and_increment_quota(user_id: str, user_plan: str) -> dict:
    """
    Check if user has remaining monthly quota. If yes, increment and return usage info.
    Raises 429 if quota exceeded.
    Returns dict with 'used' and 'limit' for informational purposes.
    """
    limit = PLAN_MONTHLY_LIMITS.get(user_plan, 10)
    current_month = datetime.utcnow().strftime("%Y-%m")

    tracker = _usage_tracker[user_id]

    # Reset counter if new month
    if tracker["month"] != current_month:
        tracker["month"] = current_month
        tracker["count"] = 0

    # Unlimited plan
    if limit == -1:
        tracker["count"] += 1
        return {"used": tracker["count"], "limit": -1}

    if tracker["count"] >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Monthly quota exceeded. Your '{user_plan}' plan allows {limit} "
                   f"AI queries per month. Used: {tracker['count']}/{limit}. "
                   f"Upgrade your plan for higher limits.",
        )

    tracker["count"] += 1
    return {"used": tracker["count"], "limit": limit}


def get_quota_usage(user_id: str, user_plan: str) -> dict:
    """Get current quota usage without incrementing."""
    limit = PLAN_MONTHLY_LIMITS.get(user_plan, 10)
    current_month = datetime.utcnow().strftime("%Y-%m")
    tracker = _usage_tracker.get(user_id, {"month": "", "count": 0})
    count = tracker["count"] if tracker["month"] == current_month else 0
    return {"used": count, "limit": limit}


# ---------------------------------------------------------------------------
# Rate Limiting (in-memory, per-user, per-minute)
# ---------------------------------------------------------------------------

# Requests per minute per plan
PLAN_RATE_LIMITS: dict[str, int] = {
    "free": 10,
    "researcher": 30,
    "lab": 60,
    "admin": 120,
}

# In-memory store: user_id -> list of request timestamps
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(user_id: str, user_plan: str) -> dict:
    """
    Check per-user per-minute rate limit. Raises 429 if exceeded.
    Returns dict with rate limit info for response headers.
    """
    max_rpm = PLAN_RATE_LIMITS.get(user_plan, 10)
    now = time.time()
    window_start = now - 60.0

    # Prune old entries
    timestamps = _rate_limit_store[user_id]
    _rate_limit_store[user_id] = [t for t in timestamps if t > window_start]
    timestamps = _rate_limit_store[user_id]

    if len(timestamps) >= max_rpm:
        retry_after = int(timestamps[0] - window_start) + 1
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Your '{user_plan}' plan allows {max_rpm} "
                   f"requests per minute. Please retry after {retry_after} seconds.",
            headers={"Retry-After": str(retry_after)},
        )

    timestamps.append(now)
    remaining = max_rpm - len(timestamps)
    return {
        "limit": max_rpm,
        "remaining": remaining,
        "reset": int(window_start + 60),
    }


# ---------------------------------------------------------------------------
# Mock user store accessor (used by routers that need user plan info)
# ---------------------------------------------------------------------------

def get_user_plan(user_id: str) -> str:
    """
    Look up the user's subscription plan. In production this would query the DB.
    Falls back to 'free' if user not found.
    """
    # Import here to avoid circular imports at module level
    from app.routers.auth import MOCK_USERS
    for user_data in MOCK_USERS.values():
        if user_data.get("id") == user_id:
            return user_data.get("role", "free")
    return "free"
