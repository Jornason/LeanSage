"""
Tactic explanation tests.
Covers: P01-P06, P08-AUTH
"""
import pytest

# Lean 4 code with 'by' at the start of a new line (required by current parser)
CODE_RING_SIMP = "theorem foo : 1 + 1 = 2 :=\nby\n  ring\n  simp"
CODE_OMEGA     = "theorem bar (n : Nat) : n + 1 > n :=\nby\n  omega"
CODE_TRIVIAL   = "theorem baz : True :=\nby\n  trivial"


@pytest.mark.explain
def test_explain_known_tactics_en(client, admin_headers):
    """P01/P02: Known tactics (ring, simp) are explained from dictionary."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    names = [s["tactic"] for s in steps]
    assert any(t in names for t in ("ring", "simp"))


@pytest.mark.explain
def test_explain_omega(client, admin_headers):
    """P03: omega tactic explanation is non-empty."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    omega_step = next((s for s in steps if s["tactic"] == "omega"), None)
    assert omega_step is not None
    assert len(omega_step["explanation"]) > 10


@pytest.mark.explain
def test_explain_language_zh(client, admin_headers):
    """P04: language=zh is echoed back in response."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "zh"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["language"] == "zh"


@pytest.mark.explain
def test_explain_language_en(client, admin_headers):
    """P05: language=en is echoed back in response."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_OMEGA, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert r.json()["data"]["language"] == "en"


@pytest.mark.explain
@pytest.mark.ai
def test_explain_unknown_tactic_uses_ai(client, admin_headers):
    """P06: Unknown tactic (trivial) falls back to AI for explanation."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_TRIVIAL, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    steps = r.json()["data"]["steps"]
    trivial = next((s for s in steps if s["tactic"] == "trivial"), None)
    assert trivial is not None, f"trivial not found in steps: {[s['tactic'] for s in steps]}"
    assert len(trivial["explanation"]) > 10


@pytest.mark.explain
def test_explain_summary_present(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 200
    assert "summary" in r.json()["data"]


@pytest.mark.explain
def test_explain_known_tactics_have_doc_url(client, admin_headers):
    """ring, simp, omega, linarith, norm_num have documentation URLs."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"},
                    headers=admin_headers)
    steps = r.json()["data"]["steps"]
    ring_step = next((s for s in steps if s["tactic"] == "ring"), None)
    if ring_step:
        assert ring_step.get("doc_url") is not None


@pytest.mark.explain
def test_explain_detailed_requires_researcher(client, demo_headers):
    """P08: Researcher plan can access detail_level=detailed."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en",
                          "detail_level": "detailed"},
                    headers=demo_headers)
    assert r.status_code == 200


@pytest.mark.explain
def test_explain_detailed_blocked_for_free(client, free_user):
    """P08: Free plan cannot access detailed explanations."""
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en",
                          "detail_level": "detailed"},
                    headers=free_user["headers"])
    assert r.status_code in (402, 403, 429)


@pytest.mark.explain
def test_explain_requires_auth(client):
    r = client.post("/v1/explain/tactics",
                    json={"code": CODE_RING_SIMP, "language": "en"})
    assert r.status_code in (401, 403)


@pytest.mark.explain
def test_explain_empty_code_returns_422(client, admin_headers):
    r = client.post("/v1/explain/tactics",
                    json={"code": "", "language": "en"},
                    headers=admin_headers)
    assert r.status_code == 422
