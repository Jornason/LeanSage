"""
Authentication Router
POST /v1/auth/login
POST /v1/auth/register
GET  /v1/auth/github
GET  /v1/auth/github/callback
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, status

from app.schemas.api import LoginRequest, RegisterRequest, TokenResponse, UserInfo
from app.schemas.common import ok, error as err
from app.core.auth import hash_password, verify_password, create_access_token
from app.core.config import settings

router = APIRouter()

# Mock user store (replace with database in production)
MOCK_USERS: dict = {}

# Pre-populate a demo user
DEMO_USER = {
    "id": "user_demo_123",
    "email": "demo@leanprove.ai",
    "display_name": "Demo Researcher",
    "role": "researcher",
    "avatar_url": None,
    "github_id": None,
    "locale": "en",
    "created_at": "2026-01-01T00:00:00Z",
}
MOCK_USERS["demo@leanprove.ai"] = {
    **DEMO_USER,
    "password_hash": hash_password("demo12345"),
}


def _make_user_info(user_data: dict) -> UserInfo:
    """Build a UserInfo schema from raw user dict, excluding sensitive fields."""
    return UserInfo(
        id=user_data["id"],
        email=user_data["email"],
        display_name=user_data["display_name"],
        role=user_data.get("role", "free"),
        avatar_url=user_data.get("avatar_url"),
        locale=user_data.get("locale", "en"),
        created_at=user_data.get("created_at", ""),
    )


@router.post("/auth/login")
async def login(request: LoginRequest):
    """Authenticate user with email/password. Returns JWT access token."""
    user = MOCK_USERS.get(request.email)
    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token(data={"sub": user["id"]})
    user_info = _make_user_info(user)

    return ok(TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=user_info,
    ).model_dump())


@router.post("/auth/register")
async def register(request: RegisterRequest):
    """Register a new user account."""
    if request.email in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user_id = f"user_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat() + "Z"
    new_user = {
        "id": user_id,
        "email": request.email,
        "display_name": request.display_name,
        "role": "free",
        "avatar_url": None,
        "github_id": None,
        "locale": request.locale,
        "created_at": now,
        "password_hash": hash_password(request.password),
    }
    MOCK_USERS[request.email] = new_user

    token = create_access_token(data={"sub": user_id})
    user_info = _make_user_info(new_user)

    return ok(TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=user_info,
    ).model_dump())


@router.post("/auth/demo")
async def demo_login():
    """Instant demo access — no registration required. Returns a demo JWT token."""
    user = MOCK_USERS["demo@leanprove.ai"]
    token = create_access_token(data={"sub": user["id"]})
    user_info = _make_user_info(user)
    return ok(TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=user_info,
    ).model_dump())


@router.get("/auth/github")
async def github_oauth_start():
    """Redirect to GitHub OAuth. (Mock endpoint)"""
    return ok({
        "redirect_url": "https://github.com/login/oauth/authorize?client_id=your-client-id&scope=user:email",
    })


@router.get("/auth/github/callback")
async def github_oauth_callback(code: str):
    """Handle GitHub OAuth callback. (Mock endpoint)"""
    # In production: exchange code for token, get user info, upsert user
    mock_user = {
        "id": "user_github_mock",
        "email": "github@example.com",
        "display_name": "GitHub User",
        "role": "free",
        "avatar_url": None,
        "locale": "en",
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    token = create_access_token(data={"sub": mock_user["id"]})
    user_info = _make_user_info(mock_user)

    return ok(TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.JWT_EXPIRE_MINUTES * 60,
        user=user_info,
    ).model_dump())
