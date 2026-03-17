"""
Authentication & security tests.
Covers: A01-A03, AU01-AU05, AUTH-01 to AUTH-04
"""
import random
import pytest


# ── Login ──────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.auth
def test_admin_login_success(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.status_code == 200
    data = r.json()["data"]
    assert "access_token" in data
    assert data["user"]["role"] == "admin"


@pytest.mark.smoke
@pytest.mark.auth
def test_demo_login_success(client):
    r = client.post("/v1/auth/login", json={
        "email": "demo@leanprove.ai", "password": "demo12345"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]


@pytest.mark.auth
def test_login_wrong_password_returns_401(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "wrongpassword99"
    })
    assert r.status_code == 401


@pytest.mark.auth
def test_login_unknown_email_returns_401(client):
    r = client.post("/v1/auth/login", json={
        "email": "nobody@nowhere.com", "password": "password123"
    })
    assert r.status_code == 401


@pytest.mark.auth
def test_login_missing_fields_returns_422(client):
    r = client.post("/v1/auth/login", json={"email": "admin@leanprove.ai"})
    assert r.status_code == 422


# ── Demo endpoint ──────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.auth
def test_demo_endpoint_returns_token(client):
    """A01: /auth/demo provides instant token without credentials."""
    r = client.post("/v1/auth/demo")
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]


# ── Registration ───────────────────────────────────────────────────────────────

@pytest.mark.auth
def test_register_new_user(client):
    """A02: Valid registration creates account and returns token."""
    email = f"reg_{random.randint(10000, 99999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "SecurePass99!", "display_name": "Tester"
    })
    assert r.status_code == 200
    assert r.json()["success"] is True
    assert "access_token" in r.json()["data"]


@pytest.mark.auth
def test_register_duplicate_email_returns_409(client):
    """AU02: Second registration with same email returns 409."""
    email = f"dup_{random.randint(10000, 99999)}@test-leansage.com"
    payload = {"email": email, "password": "SecurePass99!", "display_name": "Tester"}
    client.post("/v1/auth/register", json=payload)
    r = client.post("/v1/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.auth
def test_register_invalid_email_returns_422(client):
    """AU01: Non-email string rejected with 422."""
    r = client.post("/v1/auth/register", json={
        "email": "not-an-email", "password": "SecurePass99!", "display_name": "X"
    })
    assert r.status_code == 422


@pytest.mark.auth
def test_register_short_password_returns_422(client):
    """AU05: Password < 8 characters is rejected."""
    email = f"short_{random.randint(1, 9999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "123", "display_name": "X"
    })
    assert r.status_code == 422


@pytest.mark.auth
def test_register_missing_display_name_returns_422(client):
    email = f"nodname_{random.randint(1, 9999)}@test-leansage.com"
    r = client.post("/v1/auth/register", json={
        "email": email, "password": "SecurePass99!"
    })
    assert r.status_code == 422


# ── JWT validation ─────────────────────────────────────────────────────────────

@pytest.mark.auth
def test_invalid_token_returns_401(client):
    """AU03: Malformed / expired token is rejected."""
    r = client.get("/v1/user/profile",
                   headers={"Authorization": "Bearer invalid.jwt.token"})
    assert r.status_code == 401


@pytest.mark.auth
def test_missing_token_returns_401_or_403(client):
    """AUTH-04: No token at all is rejected."""
    r = client.get("/v1/user/profile")
    assert r.status_code in (401, 403)


@pytest.mark.auth
def test_token_type_is_bearer(client, admin_token):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.json()["data"]["token_type"].lower() == "bearer"


@pytest.mark.auth
def test_token_expires_in_7_days(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    expires_in = r.json()["data"].get("expires_in", 0)
    # 7 days = 604800 seconds (allow ±60s)
    assert abs(expires_in - 604800) < 60 or expires_in == 10080  # minutes variant
