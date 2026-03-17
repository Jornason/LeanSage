"""
Shared pytest fixtures for LeanSage API test suite.

Configuration (env vars or .env.test):
  BASE_URL          Target server  (default: http://localhost:9019)
  ADMIN_EMAIL       Admin email    (default: admin@leanprove.ai)
  ADMIN_PASSWORD    Admin password (default: admin12345)
  DEMO_EMAIL        Demo email     (default: demo@leanprove.ai)
  DEMO_PASSWORD     Demo password  (default: demo12345)
"""

import os
import pytest
import httpx
from dotenv import load_dotenv

# Load .env.test if present (never overrides real env vars)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env.test"), override=False)

# ── Configuration ──────────────────────────────────────────────────────────────

BASE_URL       = os.environ.get("BASE_URL",       "http://localhost:9019")
ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL",    "admin@leanprove.ai")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin12345")
DEMO_EMAIL     = os.environ.get("DEMO_EMAIL",     "demo@leanprove.ai")
DEMO_PASSWORD  = os.environ.get("DEMO_PASSWORD",  "demo12345")

# ── HTTP client ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client() -> httpx.Client:
    """Shared HTTP client for the whole test session."""
    with httpx.Client(base_url=BASE_URL, timeout=90.0) as c:
        yield c

# ── Token fixtures (session-scoped: login once per run) ───────────────────────

@pytest.fixture(scope="session")
def admin_token(client: httpx.Client) -> str:
    r = client.post("/v1/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD,
    })
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="session")
def demo_token(client: httpx.Client) -> str:
    r = client.post("/v1/auth/login", json={
        "email": DEMO_EMAIL,
        "password": DEMO_PASSWORD,
    })
    assert r.status_code == 200, f"Demo login failed: {r.text}"
    return r.json()["data"]["access_token"]


@pytest.fixture(scope="session")
def demo_direct_token(client: httpx.Client) -> str:
    """Token via /auth/demo (no credentials required)."""
    r = client.post("/v1/auth/demo")
    assert r.status_code == 200, f"/auth/demo failed: {r.text}"
    return r.json()["data"]["access_token"]


# ── Auth header helpers ────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def admin_headers(admin_token: str) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="session")
def demo_headers(demo_token: str) -> dict:
    return {"Authorization": f"Bearer {demo_token}"}


# ── Fresh free-plan user (function-scoped: new user per test that needs it) ───

@pytest.fixture()
def free_user(client: httpx.Client):
    """Register a fresh free-plan user and return (email, password, token)."""
    import random, string
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    email = f"free_{suffix}@test-leansage.com"
    password = "FreePass99!"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": password, "display_name": "FreeUser",
    })
    assert r.status_code == 200, f"Free user registration failed: {r.text}"
    token = r.json()["data"]["access_token"]
    return {"email": email, "password": password, "token": token,
            "headers": {"Authorization": f"Bearer {token}"}}
