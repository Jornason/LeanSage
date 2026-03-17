"""
Smoke test suite — fast sanity checks, always run first.
Target: < 10 seconds total. No AI calls.
Covers the most critical path: health, auth, search, core endpoints.
"""
import pytest


# ── Health ─────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_service_is_up(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "healthy"


@pytest.mark.smoke
def test_environment_is_production(client):
    r = client.get("/health")
    assert r.json()["environment"] == "production"


# ── Auth ───────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_admin_login(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "admin12345"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]


@pytest.mark.smoke
def test_demo_auto_login(client):
    r = client.post("/v1/auth/demo")
    assert r.status_code == 200
    assert "access_token" in r.json()["data"]


@pytest.mark.smoke
def test_bad_credentials_rejected(client):
    r = client.post("/v1/auth/login", json={
        "email": "admin@leanprove.ai", "password": "wrongpassword99"
    })
    assert r.status_code == 401


# ── Search ─────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_search_returns_results(client, admin_headers):
    r = client.post("/v1/search/mathlib",
                    json={"query": "commutativity addition", "top_k": 3},
                    headers=admin_headers)
    assert r.status_code == 200
    assert len(r.json()["data"]["results"]) >= 1


@pytest.mark.smoke
def test_search_requires_auth(client):
    r = client.post("/v1/search/mathlib",
                    json={"query": "addition", "top_k": 3})
    assert r.status_code in (401, 403)


# ── Explain (no AI — known tactic from dictionary) ─────────────────────────────

@pytest.mark.smoke
def test_explain_known_tactic(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": "theorem f :=\nby\n  ring", "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["success"] is True


# ── User ───────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_profile_accessible(client, admin_headers):
    r = client.get("/v1/user/profile", headers=admin_headers)
    assert r.status_code == 200


@pytest.mark.smoke
def test_usage_accessible(client, admin_headers):
    r = client.get("/v1/user/usage", headers=admin_headers)
    assert r.status_code == 200


# ── Convert (no AI) ────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_lean_to_latex(client, admin_headers):
    r = client.post("/v1/convert/lean-to-latex",
                    json={"lean_code": "∀ x : ℝ, x ≥ 0"},
                    headers=admin_headers)
    assert r.status_code == 200


# ── Compile (mock) ─────────────────────────────────────────────────────────────

@pytest.mark.smoke
def test_compile_check(client, admin_headers):
    r = client.post("/v1/compile/check",
                    json={"code": "theorem t : True := trivial"},
                    headers=admin_headers)
    assert r.status_code == 200
