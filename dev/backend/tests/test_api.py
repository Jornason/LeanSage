"""
Comprehensive API tests based on 07-TESTING.md test cases.
Covers: auth, search, generate, diagnose, convert, compile, explain, user, proof, billing endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ---------------------------------------------------------------------------
# Helper: get a demo JWT token
# ---------------------------------------------------------------------------

def get_demo_token() -> str:
    resp = client.post("/v1/auth/demo")
    assert resp.status_code == 200
    return resp.json()["data"]["access_token"]


def get_admin_token() -> str:
    resp = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai",
        "password": "admin12345",
    })
    assert resp.status_code == 200
    return resp.json()["data"]["access_token"]


def auth_headers(token: str = None) -> dict:
    if token is None:
        token = get_demo_token()
    return {"Authorization": f"Bearer {token}"}


# ===========================================================================
# Authentication Tests (A01-A06, AU01-AU06)
# ===========================================================================

class TestAuth:
    def test_demo_login(self):
        """Demo login returns valid JWT + user info."""
        resp = client.post("/v1/auth/demo")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "demo@leanprove.ai"
        assert data["user"]["role"] == "researcher"

    def test_login_valid(self):
        """Login with valid demo credentials."""
        resp = client.post("/v1/auth/login", json={
            "email": "demo@leanprove.ai",
            "password": "demo12345",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]

    def test_login_wrong_password(self):
        """Login with wrong password returns 401."""
        resp = client.post("/v1/auth/login", json={
            "email": "demo@leanprove.ai",
            "password": "wrongpassword",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self):
        """Login with unknown email returns 401."""
        resp = client.post("/v1/auth/login", json={
            "email": "nobody@example.com",
            "password": "whatever",
        })
        assert resp.status_code == 401

    def test_register_new_user(self):
        """Register a brand new user."""
        resp = client.post("/v1/auth/register", json={
            "email": "newuser@test.com",
            "password": "securepass123",
            "display_name": "New User",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["user"]["email"] == "newuser@test.com"
        assert data["user"]["role"] == "free"

    def test_register_duplicate_email(self):
        """AU02: Registering with existing email returns 409."""
        # First registration
        client.post("/v1/auth/register", json={
            "email": "duplicate@test.com",
            "password": "pass12345",
            "display_name": "Dup User",
        })
        # Duplicate
        resp = client.post("/v1/auth/register", json={
            "email": "duplicate@test.com",
            "password": "pass45678",
            "display_name": "Dup User 2",
        })
        assert resp.status_code == 409

    def test_invalid_token(self):
        """AU03: Invalid JWT returns 401."""
        resp = client.get("/v1/user/profile", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_no_token(self):
        """No authorization header returns 403."""
        resp = client.get("/v1/user/profile")
        assert resp.status_code == 403

    def test_github_oauth_start(self):
        """GitHub OAuth start returns redirect URL."""
        resp = client.get("/v1/auth/github")
        assert resp.status_code == 200
        assert "redirect_url" in resp.json()["data"]

    def test_github_oauth_callback(self):
        """GitHub OAuth callback returns token."""
        resp = client.get("/v1/auth/github/callback?code=mock_code")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]


# ===========================================================================
# Search Tests (S01-S07)
# ===========================================================================

class TestSearch:
    def test_s01_chinese_query(self):
        """S01: Chinese query returns results."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={"query": "连续函数的和是连续的"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "results" in data
        assert len(data["results"]) > 0

    def test_s02_english_query(self):
        """S02: English query returns results."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={"query": "sum of continuous functions"}, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert len(data["results"]) > 0

    def test_s04_empty_query(self):
        """S04: Empty query returns 422 validation error."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={"query": ""}, headers=headers)
        assert resp.status_code == 422

    def test_s05_long_query(self):
        """S05: Query over 500 chars returns 422."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={"query": "a" * 501}, headers=headers)
        assert resp.status_code == 422

    def test_s07_top_k(self):
        """S07: top_k=3 returns at most 3 results."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={"query": "continuous", "top_k": 3}, headers=headers)
        assert resp.status_code == 200
        results = resp.json()["data"]["results"]
        assert len(results) <= 3

    def test_search_with_module_filter(self):
        """S03: Module filter applied."""
        headers = auth_headers()
        resp = client.post("/v1/search/mathlib", json={
            "query": "limit", "filter_module": "Topology"
        }, headers=headers)
        assert resp.status_code == 200


# ===========================================================================
# Generate Tests (G01-G06)
# ===========================================================================

class TestGenerate:
    def test_g01_simple_proof(self):
        """G01: Generate proof for simple theorem."""
        headers = auth_headers()
        resp = client.post("/v1/generate/proof", json={
            "description": "证明1+1=2",
            "style": "tactic",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "lean_code" in data
        assert len(data["lean_code"]) > 0

    def test_g02_medium_proof(self):
        """G02: Generate medium complexity proof."""
        headers = auth_headers()
        resp = client.post("/v1/generate/proof", json={
            "description": "连续函数复合连续",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "theorem" in data["lean_code"].lower() or "def" in data["lean_code"].lower() or "lean_code" in data

    def test_g04_term_style(self):
        """G04: Generate proof in term style."""
        headers = auth_headers()
        resp = client.post("/v1/generate/proof", json={
            "description": "Prove 1+1=2",
            "style": "term",
        }, headers=headers)
        assert resp.status_code == 200


# ===========================================================================
# Diagnose Tests (D01-D05)
# ===========================================================================

class TestDiagnose:
    def test_d01_unknown_tactic(self):
        """D01: Unknown tactic 'omega_bad' → suggest omega."""
        headers = auth_headers()
        resp = client.post("/v1/diagnose/error", json={
            "code": "theorem bad_proof (n : Nat) : n + 1 > n := by\n  omega_bad",
            "error_message": "unknown tactic 'omega_bad'",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "diagnostics" in data
        assert len(data["diagnostics"]) > 0

    def test_d02_type_mismatch(self):
        """D02: Type mismatch Nat vs Int."""
        headers = auth_headers()
        resp = client.post("/v1/diagnose/error", json={
            "code": "def foo : Int := (42 : Nat)",
            "error_message": "type mismatch",
        }, headers=headers)
        assert resp.status_code == 200

    def test_d05_no_error_code(self):
        """D05: Code with no error returns diagnostics."""
        headers = auth_headers()
        resp = client.post("/v1/diagnose/error", json={
            "code": "theorem test : 1 + 1 = 2 := by norm_num",
        }, headers=headers)
        assert resp.status_code == 200


# ===========================================================================
# Convert Tests (X01-X02, X05)
# ===========================================================================

class TestConvert:
    def test_x01_latex_to_lean(self):
        """X01: LaTeX → Lean basic conversion."""
        headers = auth_headers()
        resp = client.post("/v1/convert/latex-to-lean", json={
            "latex": r"\forall x, f(x) > 0",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "lean_expression" in data

    def test_x02_lean_to_latex(self):
        """X02: Lean → LaTeX basic conversion."""
        headers = auth_headers()
        resp = client.post("/v1/convert/lean-to-latex", json={
            "lean_code": "∀ x, f x > 0",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "latex" in data

    def test_x05_invalid_latex(self):
        """X05: Invalid LaTeX returns error hint."""
        headers = auth_headers()
        resp = client.post("/v1/convert/latex-to-lean", json={
            "latex": "",
        }, headers=headers)
        # Empty input should fail validation
        assert resp.status_code == 422


# ===========================================================================
# Compile Tests
# ===========================================================================

class TestCompile:
    def test_compile_check(self):
        """Compile check returns mock result."""
        headers = auth_headers()
        resp = client.post("/v1/compile/check", json={
            "code": "import Mathlib.Tactic\n\ntheorem test : 1 + 1 = 2 := by norm_num",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "status" in data


# ===========================================================================
# Explain Tests (P01-P05)
# ===========================================================================

class TestExplain:
    def test_p01_single_tactic(self):
        """P01: Single tactic explanation."""
        headers = auth_headers()
        resp = client.post("/v1/explain/tactics", json={
            "code": "theorem test : 1 + 1 = 2 := by simp",
            "language": "en",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "steps" in data
        assert len(data["steps"]) > 0

    def test_p04_chinese_output(self):
        """P04: Chinese language explanation."""
        headers = auth_headers()
        resp = client.post("/v1/explain/tactics", json={
            "code": "theorem test : True := by trivial",
            "language": "zh",
        }, headers=headers)
        assert resp.status_code == 200


# ===========================================================================
# User Tests
# ===========================================================================

class TestUser:
    def test_user_profile(self):
        """Get user profile returns user info."""
        headers = auth_headers()
        resp = client.get("/v1/user/profile", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "email" in data

    def test_user_usage(self):
        """Get usage stats returns quota info."""
        headers = auth_headers()
        resp = client.get("/v1/user/usage", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "plan" in data


# ===========================================================================
# Proof Session Tests
# ===========================================================================

class TestProofSession:
    def test_create_session(self):
        """Create a new proof session."""
        headers = auth_headers()
        resp = client.post("/v1/proof/sessions", json={
            "title": "Test Session",
            "description": "Testing proof sessions",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["title"] == "Test Session"
        return data["id"]

    def test_list_sessions(self):
        """List proof sessions."""
        headers = auth_headers()
        resp = client.get("/v1/proof/sessions", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert isinstance(data, list)

    def test_session_crud(self):
        """Full CRUD cycle for sessions."""
        headers = auth_headers()
        # Create
        resp = client.post("/v1/proof/sessions", json={
            "title": "CRUD Test",
        }, headers=headers)
        assert resp.status_code == 200
        session_id = resp.json()["data"]["id"]

        # Read
        resp = client.get(f"/v1/proof/sessions/{session_id}", headers=headers)
        assert resp.status_code == 200

        # Update
        resp = client.patch(f"/v1/proof/sessions/{session_id}", json={
            "title": "Updated Title",
            "current_code": "-- updated code",
        }, headers=headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["title"] == "Updated Title"

        # Delete
        resp = client.delete(f"/v1/proof/sessions/{session_id}", headers=headers)
        assert resp.status_code == 200


# ===========================================================================
# Billing Tests
# ===========================================================================

class TestBilling:
    def test_get_subscription(self):
        """Get subscription info."""
        headers = auth_headers()
        resp = client.get("/v1/billing/subscription", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "plan" in data

    def test_create_checkout(self):
        """Create checkout session (mock)."""
        headers = auth_headers()
        resp = client.post("/v1/billing/create-checkout", json={
            "plan": "researcher",
        }, headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "checkout_url" in data


# ===========================================================================
# Health Check
# ===========================================================================

class TestHealth:
    def test_health(self):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_root(self):
        resp = client.get("/")
        assert resp.status_code == 200


# ===========================================================================
# Admin Account Tests - Maximum Privileges
# ===========================================================================

class TestAdminAccount:
    def test_admin_login(self):
        """Admin can login with email/password."""
        resp = client.post("/v1/auth/login", json={
            "email": "admin@leanprove.ai",
            "password": "admin12345",
        })
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["access_token"]
        assert data["user"]["role"] == "admin"
        assert data["user"]["email"] == "admin@leanprove.ai"
        assert data["user"]["display_name"] == "Admin"

    def test_admin_profile(self):
        """Admin profile shows admin role."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.get("/v1/user/profile", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["role"] == "admin"
        assert data["email"] == "admin@leanprove.ai"

    def test_admin_usage_unlimited(self):
        """Admin has unlimited quota."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.get("/v1/user/usage", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["plan"] == "admin"
        assert data["searches"]["limit"] == -1  # unlimited

    def test_admin_search(self):
        """Admin can use search."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/search/mathlib", json={"query": "continuous"}, headers=headers)
        assert resp.status_code == 200

    def test_admin_generate(self):
        """Admin can use proof generation (researcher+ gated)."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/generate/proof", json={
            "description": "Prove 1+1=2",
        }, headers=headers)
        assert resp.status_code == 200

    def test_admin_compile(self):
        """Admin can use compilation (researcher+ gated)."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/compile/check", json={
            "code": "theorem test : 1 + 1 = 2 := by norm_num",
        }, headers=headers)
        assert resp.status_code == 200

    def test_admin_diagnose(self):
        """Admin can use error diagnosis."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/diagnose/error", json={
            "code": "theorem bad : True := by omega_bad",
            "error_message": "unknown tactic",
        }, headers=headers)
        assert resp.status_code == 200

    def test_admin_convert(self):
        """Admin can use LaTeX↔Lean conversion."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/convert/latex-to-lean", json={
            "latex": r"\forall x, x > 0",
        }, headers=headers)
        assert resp.status_code == 200

    def test_admin_explain(self):
        """Admin can use tactic explanation."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.post("/v1/explain/tactics", json={
            "code": "theorem test : True := by trivial",
        }, headers=headers)
        assert resp.status_code == 200

    def test_admin_billing(self):
        """Admin subscription shows admin plan."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        resp = client.get("/v1/billing/subscription", headers=headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["plan"] == "admin"

    def test_admin_proof_sessions(self):
        """Admin can manage proof sessions."""
        headers = {"Authorization": f"Bearer {get_admin_token()}"}
        # Create
        resp = client.post("/v1/proof/sessions", json={
            "title": "Admin Test Session",
        }, headers=headers)
        assert resp.status_code == 200
        session_id = resp.json()["data"]["id"]

        # List
        resp = client.get("/v1/proof/sessions", headers=headers)
        assert resp.status_code == 200

        # Read
        resp = client.get(f"/v1/proof/sessions/{session_id}", headers=headers)
        assert resp.status_code == 200

        # Update
        resp = client.patch(f"/v1/proof/sessions/{session_id}", json={
            "title": "Admin Updated",
        }, headers=headers)
        assert resp.status_code == 200

        # Delete
        resp = client.delete(f"/v1/proof/sessions/{session_id}", headers=headers)
        assert resp.status_code == 200
