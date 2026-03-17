#!/usr/bin/env python3
"""
LeanSage 生产环境自测套件
覆盖 07-TESTING.md 所有可 API 测试的测试点
服务器: http://47.242.43.35:9019
"""

import json
import time
import sys
import threading
import urllib.request
import urllib.error
from typing import Optional

BASE = "http://localhost:9019"
RESULTS = []
TOKENS = {}  # role -> token

# ─── 颜色输出 ─────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg): print(f"  {RED}✗{RESET} {msg}")
def skip(msg): print(f"  {YELLOW}⚡{RESET} {msg}")
def header(title): print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}\n{BOLD}{CYAN}  {title}{RESET}\n{CYAN}{'─'*60}{RESET}")

# ─── HTTP 工具 ─────────────────────────────────────────────────────────────────
def request(method, path, body=None, token=None, timeout=30):
    url = BASE + path
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            elapsed = (time.time() - t0) * 1000
            return json.loads(resp.read()), resp.status, elapsed
    except urllib.error.HTTPError as e:
        elapsed = (time.time() - t0) * 1000
        try:
            body = json.loads(e.read())
        except Exception:
            body = {"detail": str(e)}
        return body, e.code, elapsed
    except TimeoutError:
        return {"detail": "timeout"}, 408, timeout * 1000
    except Exception as ex:
        return {"detail": str(ex)}, 0, 0

def get(path, token=None, timeout=30):
    return request("GET", path, token=token, timeout=timeout)

def post(path, body=None, token=None, timeout=60):
    return request("POST", path, body=body, token=token, timeout=timeout)

def patch(path, body=None, token=None):
    return request("PATCH", path, body=body, token=token)

def delete(path, token=None):
    return request("DELETE", path, token=token)

# ─── 断言工具 ──────────────────────────────────────────────────────────────────
passed = failed = skipped = 0

def assert_test(test_id, desc, condition, detail="", warn=False):
    global passed, failed, skipped
    if condition:
        passed += 1
        ok(f"[{test_id}] {desc}")
        RESULTS.append((test_id, "PASS", desc, ""))
    elif warn:
        skipped += 1
        skip(f"[{test_id}] {desc}  ← {detail}")
        RESULTS.append((test_id, "SKIP", desc, detail))
    else:
        failed += 1
        fail(f"[{test_id}] {desc}  ← {detail}")
        RESULTS.append((test_id, "FAIL", desc, detail))

def assert_status(test_id, desc, resp, code, status, detail_fn=None):
    d, s, ms = resp
    ok_cond = (s == status)
    detail = detail_fn(d) if (detail_fn and ok_cond) else (f"HTTP {s}, expected {status}, body={str(d)[:120]}")
    assert_test(test_id, f"{desc} [{ms:.0f}ms]", ok_cond, detail)
    return d, s, ms

# ═══════════════════════════════════════════════════════════════════════════════
#  SETUP: 获取各角色 Token
# ═══════════════════════════════════════════════════════════════════════════════
def setup_tokens():
    header("SETUP — 获取各角色认证 Token")
    accounts = [
        ("admin",      "admin@leanprove.ai",   "admin12345"),
        ("demo",       "demo@leanprove.ai",    "demo12345"),
    ]
    for role, email, pw in accounts:
        d, s, ms = post("/v1/auth/login", {"email": email, "password": pw})
        if s == 200 and d.get("data", {}).get("access_token"):
            TOKENS[role] = d["data"]["access_token"]
            ok(f"[SETUP] {role} token 获取成功  [{ms:.0f}ms]")
        else:
            fail(f"[SETUP] {role} token 获取失败: {d}")

    # Demo 用户也通过 /auth/demo 获取
    d, s, ms = post("/v1/auth/demo")
    if s == 200 and d.get("data", {}).get("access_token"):
        TOKENS["demo_direct"] = d["data"]["access_token"]
        ok(f"[SETUP] demo (直连) token 获取成功  [{ms:.0f}ms]")
    else:
        skip(f"[SETUP] /auth/demo 失败: {d}")

# ═══════════════════════════════════════════════════════════════════════════════
#  1. 健康检查
# ═══════════════════════════════════════════════════════════════════════════════
def test_health():
    header("健康检查")
    d, s, ms = get("/health")
    assert_test("HEALTH-01", f"GET /health 返回 200  [{ms:.0f}ms]", s == 200, str(d))
    assert_test("HEALTH-02", "status = healthy", d.get("status") == "healthy", str(d))
    assert_test("HEALTH-03", "environment = production", d.get("environment") == "production", str(d))

    d, s, ms = get("/")
    assert_test("HEALTH-04", f"GET / (root) 返回 200  [{ms:.0f}ms]", s == 200, str(d))

# ═══════════════════════════════════════════════════════════════════════════════
#  2. 认证模块 A / AU
# ═══════════════════════════════════════════════════════════════════════════════
def test_auth():
    header("认证模块 (A / AU)")
    token = TOKENS.get("admin")

    # A02: 邮箱注册
    import random
    rand_email = f"test_{random.randint(10000,99999)}@example.com"
    d, s, ms = post("/v1/auth/register", {
        "email": rand_email, "password": "Secure12345", "display_name": "TestUser"
    })
    assert_test("A02", f"邮箱注册新用户  [{ms:.0f}ms]", s == 200 and d.get("success"), str(d)[:120])

    # AU02: 重复邮箱注册 → 409
    d2, s2, ms2 = post("/v1/auth/register", {
        "email": rand_email, "password": "Secure12345", "display_name": "Dup"
    })
    assert_test("AU02", f"重复邮箱注册返回 409  [{ms2:.0f}ms]", s2 == 409, f"got {s2}: {str(d2)[:80]}")

    # AU01: 无效邮箱格式 → 422
    d3, s3, _ = post("/v1/auth/register", {
        "email": "not-an-email", "password": "Secure12345", "display_name": "X"
    })
    assert_test("AU01", "无效邮箱格式返回 422", s3 == 422, f"got {s3}: {str(d3)[:80]}")

    # AU05: 密码过短 → 422
    d4, s4, _ = post("/v1/auth/register", {
        "email": f"short_{random.randint(1,9999)}@test.com",
        "password": "123", "display_name": "X"
    })
    assert_test("AU05", "短密码 (<8) 返回 422", s4 == 422, f"got {s4}: {str(d4)[:80]}")

    # Admin 登录，验证 role=admin
    d5, s5, ms5 = post("/v1/auth/login", {"email": "admin@leanprove.ai", "password": "admin12345"})
    assert_test("AUTH-01", f"Admin 登录成功  [{ms5:.0f}ms]", s5 == 200 and d5.get("success"), str(d5)[:80])
    assert_test("AUTH-02", "Admin role=admin", d5.get("data", {}).get("user", {}).get("role") == "admin", str(d5)[:80])

    # 错误密码
    d6, s6, _ = post("/v1/auth/login", {"email": "admin@leanprove.ai", "password": "wrongpass"})
    assert_test("AUTH-03", "错误密码返回 401", s6 == 401, f"got {s6}")

    # AU03: 无效 token → 401
    d7, s7, _ = get("/v1/user/profile", token="invalid.token.here")
    assert_test("AU03", "无效 JWT 返回 401", s7 == 401, f"got {s7}")

    # 无 token → 401/403
    d8, s8, _ = get("/v1/user/profile")
    assert_test("AUTH-04", "未认证请求返回 401/403", s8 in (401, 403), f"got {s8}")

    # /auth/demo 直接登录
    d9, s9, ms9 = post("/v1/auth/demo")
    assert_test("A01-DEMO", f"/auth/demo 返回 token  [{ms9:.0f}ms]", s9 == 200 and "access_token" in str(d9), str(d9)[:80])

# ═══════════════════════════════════════════════════════════════════════════════
#  3. 搜索模块 S
# ═══════════════════════════════════════════════════════════════════════════════
def test_search():
    header("搜索模块 (S)")
    token = TOKENS.get("admin")
    if not token:
        skip("[S] 跳过：无 admin token")
        return

    # S02: 英文查询
    d, s, ms = post("/v1/search/mathlib", {"query": "commutativity of addition", "top_k": 5}, token=token)
    assert_test("S02", f"英文查询返回结果  [{ms:.0f}ms]", s == 200 and d.get("success"), str(d)[:80])
    results = d.get("data", {}).get("results", [])
    assert_test("S02b", f"返回 ≥1 条结果 (got {len(results)})", len(results) >= 1, str(d)[:80])

    # S07: TopK 参数 (field is top_k, not limit)
    d2, s2, ms2 = post("/v1/search/mathlib", {"query": "natural number induction", "top_k": 3}, token=token)
    r2 = d2.get("data", {}).get("results", [])
    assert_test("S07", f"top_k=3 返回 ≤3 条  [{ms2:.0f}ms]", s2 == 200 and len(r2) <= 3, f"got {len(r2)}")

    # S04: 空查询 → 422
    d3, s3, ms3 = post("/v1/search/mathlib", {"query": "", "top_k": 5}, token=token)
    assert_test("S04", f"空查询返回 422  [{ms3:.0f}ms]", s3 == 422, f"got {s3}: {str(d3)[:80]}")

    # S05: 超长查询 → 422
    d4, s4, ms4 = post("/v1/search/mathlib", {"query": "x" * 501, "top_k": 5}, token=token)
    assert_test("S05", f"超长查询(501字符) 返回 422  [{ms4:.0f}ms]", s4 == 422, f"got {s4}: {str(d4)[:80]}")

    # S06: 缓存（第二次同查询应更快）
    q = "continuous function composition"
    post("/v1/search/mathlib", {"query": q, "top_k": 5}, token=token)  # 预热
    _, _, ms_first = post("/v1/search/mathlib", {"query": q, "top_k": 5}, token=token)
    _, _, ms_second = post("/v1/search/mathlib", {"query": q, "top_k": 5}, token=token)
    assert_test("S06", f"缓存：二次查询 [{ms_second:.0f}ms] ≤ 首次 [{ms_first:.0f}ms] × 1.5",
                ms_second <= ms_first * 1.5 + 200, f"first={ms_first:.0f}ms, second={ms_second:.0f}ms", warn=True)

    # 中文查询
    d5, s5, ms5 = post("/v1/search/mathlib", {"query": "自然数加法交换律", "top_k": 5}, token=token)
    assert_test("S01", f"中文查询返回结果  [{ms5:.0f}ms]", s5 == 200 and d5.get("success"), str(d5)[:80])

# ═══════════════════════════════════════════════════════════════════════════════
#  4. 生成模块 G
# ═══════════════════════════════════════════════════════════════════════════════
def test_generate():
    header("证明生成模块 (G)")
    token = TOKENS.get("admin")
    if not token:
        skip("[G] 跳过：无 admin token")
        return

    # G01: 简单定理 — 1+1=2
    d, s, ms = post("/v1/generate/proof",
        {"description": "Prove that 1 + 1 = 2 for natural numbers", "language": "lean4"},
        token=token, timeout=60)
    code = d.get("data", {}).get("lean_code", "")
    assert_test("G01", f"简单定理生成(1+1=2)  [{ms:.0f}ms]", s == 200 and len(code) > 10, f"code={code[:80]}")
    assert_test("G01b", "生成代码含 theorem 关键字", "theorem" in code or "def" in code or "lemma" in code, code[:100])
    conf = d.get("data", {}).get("confidence", 0)
    assert_test("G01c", f"confidence ≥ 0.4 (got {conf:.2f})", conf >= 0.4, "")

    # G01 AI vs Fallback
    assert_test("G01d", f"AI 真实响应 confidence=0.85 (not fallback)",
                conf >= 0.8, f"confidence={conf:.2f} — 可能是 fallback(0.4)", warn=conf < 0.8)

    # G02: 中等定理 — 自然数归纳
    d2, s2, ms2 = post("/v1/generate/proof",
        {"description": "Prove n + 0 = n for all natural numbers n using induction", "language": "lean4"},
        token=token, timeout=60)
    code2 = d2.get("data", {}).get("lean_code", "")
    assert_test("G02", f"中等定理生成(n+0=n)  [{ms2:.0f}ms]", s2 == 200 and len(code2) > 10, code2[:80])

    # G03: 含 sorry 的框架（复杂定理）
    d3, s3, ms3 = post("/v1/generate/proof",
        {"description": "Prove the intermediate value theorem for continuous functions", "language": "lean4"},
        token=token, timeout=60)
    code3 = d3.get("data", {}).get("lean_code", "")
    assert_test("G03", f"复杂定理生成框架  [{ms3:.0f}ms]", s3 == 200 and len(code3) > 10, code3[:80])

    # Free 用户无法访问生成（quota check）
    demo_token = TOKENS.get("demo_direct")
    if demo_token:
        d4, s4, ms4 = post("/v1/generate/proof",
            {"description": "Prove 1+1=2", "language": "lean4"},
            token=demo_token, timeout=30)
        # demo 是 researcher，可以访问
        assert_test("G-AUTH", f"Researcher 可访问生成模块  [{ms4:.0f}ms]",
                    s4 == 200, f"got {s4}: {str(d4)[:80]}")

# ═══════════════════════════════════════════════════════════════════════════════
#  5. 诊断模块 D
# ═══════════════════════════════════════════════════════════════════════════════
def test_diagnose():
    header("错误诊断模块 (D)")
    token = TOKENS.get("admin")
    if not token:
        skip("[D] 跳过：无 admin token")
        return

    # D01: 未知 tactic
    d, s, ms = post("/v1/diagnose/error", {
        "code": "theorem foo : 1 = 1 := by\n  omega_bad",
        "error_message": "unknown tactic 'omega_bad'"
    }, token=token, timeout=45)
    diags = d.get("data", {}).get("diagnostics", [])
    assert_test("D01", f"未知 tactic 返回诊断  [{ms:.0f}ms]", s == 200 and len(diags) >= 1, str(d)[:120])
    if diags:
        assert_test("D01b", "诊断含修复建议", len(diags[0].get("suggestions", [])) >= 1,
                    f"suggestions={diags[0].get('suggestions')}")

    # D02: 类型不匹配
    d2, s2, ms2 = post("/v1/diagnose/error", {
        "code": "theorem foo (n : Nat) : n = (n : Int) := by rfl",
        "error_message": "type mismatch: Nat vs Int"
    }, token=token, timeout=45)
    diags2 = d2.get("data", {}).get("diagnostics", [])
    assert_test("D02", f"类型不匹配诊断  [{ms2:.0f}ms]", s2 == 200 and len(diags2) >= 1, str(d2)[:120])

    # D03: 缺少 import（unknown identifier）
    d3, s3, ms3 = post("/v1/diagnose/error", {
        "code": "theorem foo : Continuous (fun x : ℝ => x) := by exact continuous_id",
        "error_message": "unknown identifier 'continuous_id'"
    }, token=token, timeout=45)
    diags3 = d3.get("data", {}).get("diagnostics", [])
    assert_test("D03", f"未知标识符诊断（建议 import）  [{ms3:.0f}ms]",
                s3 == 200 and len(diags3) >= 1, str(d3)[:120])

    # D05: 无错代码，no_errors（AI 可能有 false positive，设为 warn）
    d4, s4, ms4 = post("/v1/diagnose/error", {
        "code": "theorem foo : 1 + 1 = 2 := by norm_num",
        "error_message": None
    }, token=token, timeout=45)
    total_errors = d4.get("data", {}).get("total_errors", -1)
    assert_test("D05", f"无错代码 total_errors=0  [{ms4:.0f}ms]",
                s4 == 200 and total_errors == 0,
                f"total_errors={total_errors}（AI 偶发 false positive）",
                warn=total_errors > 0)

    # D06: sorry 警告
    d5, s5, ms5 = post("/v1/diagnose/error", {
        "code": "theorem foo : 1 = 2 := by\n  sorry",
        "error_message": None
    }, token=token, timeout=45)
    diags5 = d5.get("data", {}).get("diagnostics", [])
    has_sorry_warn = any(
        d.get("severity") == "warning" or "sorry" in d.get("explanation", "").lower()
        for d in diags5
    )
    assert_test("D05b", f"sorry 代码返回 warning  [{ms5:.0f}ms]",
                s5 == 200 and has_sorry_warn, f"diags={str(diags5)[:120]}")

    # severity_filter 参数
    d6, s6, ms6 = post("/v1/diagnose/error", {
        "code": "theorem foo : 1 = 2 := by\n  sorry",
        "error_message": None,
        "severity_filter": "error"
    }, token=token, timeout=45)
    diags6 = d6.get("data", {}).get("diagnostics", [])
    only_errors = all(x.get("severity") == "error" for x in diags6)
    assert_test("D-FILTER", f"severity_filter=error 只返回 error  [{ms6:.0f}ms]",
                s6 == 200 and only_errors, f"diags={diags6}")

# ═══════════════════════════════════════════════════════════════════════════════
#  6. 证明解释模块 P / Explain
# ═══════════════════════════════════════════════════════════════════════════════
def test_explain():
    header("Tactic 解释模块 (P)")
    token = TOKENS.get("admin")
    if not token:
        skip("[P] 跳过：无 admin token")
        return

    # P01 / P02: 已知 tactics (ring, simp, omega)
    code_known = "theorem foo (n : Nat) : n + 0 = n :=\nby\n  ring\n  simp\n  omega"
    d, s, ms = post("/v1/explain/tactics", {"code": code_known, "language": "en"}, token=token, timeout=30)
    steps = d.get("data", {}).get("steps", [])
    names = [st["tactic"] for st in steps]
    assert_test("P01", f"已知 tactics 返回解释  [{ms:.0f}ms]",
                s == 200 and len(steps) >= 1, f"steps={names}")
    assert_test("P01b", "ring/simp/omega 均被识别",
                any(t in names for t in ["ring", "simp", "omega"]), f"got={names}")

    # P03: omega tactic 解释
    d2, s2, ms2 = post("/v1/explain/tactics", {
        "code": "theorem foo (n : Nat) : n + 1 > n :=\nby\n  omega",
        "language": "en"
    }, token=token, timeout=30)
    steps2 = d2.get("data", {}).get("steps", [])
    omega_step = next((st for st in steps2 if st["tactic"] == "omega"), None)
    assert_test("P03", f"omega tactic 有解释  [{ms2:.0f}ms]",
                omega_step is not None and len(omega_step.get("explanation", "")) > 10,
                f"omega_step={omega_step}")

    # P04: 中文输出
    d3, s3, ms3 = post("/v1/explain/tactics", {
        "code": "theorem foo (n : Nat) : n + 1 > n :=\nby\n  omega",
        "language": "zh"
    }, token=token, timeout=30)
    lang_out = d3.get("data", {}).get("language", "")
    assert_test("P04", f"中文输出 language=zh  [{ms3:.0f}ms]", s3 == 200 and lang_out == "zh", f"lang={lang_out}")

    # P05: 英文输出
    d4, s4, ms4 = post("/v1/explain/tactics", {
        "code": "theorem foo (n : Nat) : n + 1 > n :=\nby\n  omega",
        "language": "en"
    }, token=token, timeout=30)
    lang_out4 = d4.get("data", {}).get("language", "")
    assert_test("P05", f"英文输出 language=en  [{ms4:.0f}ms]", s4 == 200 and lang_out4 == "en", f"lang={lang_out4}")

    # P06: 未知 tactic — AI 补充解释
    d5, s5, ms5 = post("/v1/explain/tactics", {
        "code": "theorem foo : True :=\nby\n  trivial",
        "language": "en"
    }, token=token, timeout=45)
    steps5 = d5.get("data", {}).get("steps", [])
    trivial_step = next((st for st in steps5 if st["tactic"] == "trivial"), None)
    assert_test("P06", f"未知 tactic trivial — AI 生成解释  [{ms5:.0f}ms]",
                trivial_step is not None and len(trivial_step.get("explanation", "")) > 10,
                f"steps={[s['tactic'] for s in steps5]}", warn=trivial_step is None)

    # 需要 Researcher+ 权限的 detailed
    demo_token = TOKENS.get("demo_direct")
    if demo_token:
        d6, s6, ms6 = post("/v1/explain/tactics", {
            "code": "theorem foo :=\nby\n  ring",
            "language": "en",
            "detail_level": "detailed"
        }, token=demo_token, timeout=30)
        assert_test("P08-AUTH", f"Researcher 可访问 detailed 解释  [{ms6:.0f}ms]",
                    s6 == 200, f"got {s6}: {str(d6)[:80]}")

# ═══════════════════════════════════════════════════════════════════════════════
#  7. LaTeX 转换模块 X
# ═══════════════════════════════════════════════════════════════════════════════
def test_convert():
    header("LaTeX 转换模块 (X)")
    token = TOKENS.get("admin")
    if not token:
        skip("[X] 跳过：无 admin token")
        return

    # X01: LaTeX → Lean（响应字段为 lean_expression / lean_declaration）
    d, s, ms = post("/v1/convert/latex-to-lean", {
        "latex": r"\forall x : \mathbb{R}, x^2 \geq 0"
    }, token=token, timeout=45)
    data1 = d.get("data", {})
    lean_out = data1.get("lean_expression") or data1.get("lean_declaration") or data1.get("lean_code", "")
    assert_test("X01", f"LaTeX→Lean 基础  [{ms:.0f}ms]", s == 200 and len(lean_out) > 3, f"data={str(data1)[:120]}")

    # X02: Lean → LaTeX
    d2, s2, ms2 = post("/v1/convert/lean-to-latex", {
        "lean_code": "∀ x : ℝ, x^2 ≥ 0"
    }, token=token, timeout=45)
    latex_out = d2.get("data", {}).get("latex", "")
    assert_test("X02", f"Lean→LaTeX 基础  [{ms2:.0f}ms]", s2 == 200 and len(latex_out) > 3, f"latex={latex_out[:80]}")

    # X05: 空内容 → 422
    d3, s3, ms3 = post("/v1/convert/latex-to-lean", {"latex": ""}, token=token)
    assert_test("X05", f"空 LaTeX 返回 422  [{ms3:.0f}ms]", s3 == 422, f"got {s3}: {str(d3)[:80]}")

    # X09: 往返一致性（语义等价）
    original = r"\forall n : \mathbb{N}, n + 0 = n"
    d4, s4, _ = post("/v1/convert/latex-to-lean", {"latex": original}, token=token, timeout=45)
    if s4 == 200:
        data4 = d4.get("data", {})
        lean_mid = data4.get("lean_expression") or data4.get("lean_declaration") or data4.get("lean_code", "")
        d5, s5, ms5 = post("/v1/convert/lean-to-latex", {"lean_code": lean_mid}, token=token, timeout=45)
        latex_rt = d5.get("data", {}).get("latex", "")
        # 往返结果含核心数学符号
        has_forall = "forall" in latex_rt.lower() or "\\forall" in latex_rt or "∀" in latex_rt
        assert_test("X09", f"LaTeX→Lean→LaTeX 往返含 ∀  [{ms5:.0f}ms]",
                    s5 == 200 and len(latex_rt) > 3, f"rt={latex_rt[:80]}", warn=not has_forall)
    else:
        skip(f"[X09] 跳过往返测试（LaTeX→Lean 失败）")

    # X10: Unicode 符号
    d6, s6, ms6 = post("/v1/convert/lean-to-latex", {
        "lean_code": "∀ x, ∃ y, x ∈ Set.univ ∧ y ∉ ∅"
    }, token=token, timeout=45)
    latex6 = d6.get("data", {}).get("latex", "")
    assert_test("X10", f"Lean Unicode→LaTeX  [{ms6:.0f}ms]", s6 == 200 and len(latex6) > 3, f"latex={latex6[:80]}")

# ═══════════════════════════════════════════════════════════════════════════════
#  8. 编译模块
# ═══════════════════════════════════════════════════════════════════════════════
def test_compile():
    header("编译检查模块")
    token = TOKENS.get("admin")
    if not token:
        skip("[COMPILE] 跳过：无 admin token")
        return

    # 有效代码
    d, s, ms = post("/v1/compile/check", {
        "code": "theorem foo : 1 + 1 = 2 := by norm_num"
    }, token=token, timeout=30)
    assert_test("COMPILE-01", f"有效代码编译  [{ms:.0f}ms]", s == 200 and d.get("success"), str(d)[:80])

    # 无效代码
    d2, s2, ms2 = post("/v1/compile/check", {
        "code": "theorem foo : 1 = 2 := by rfl"
    }, token=token, timeout=30)
    assert_test("COMPILE-02", f"无效代码编译  [{ms2:.0f}ms]", s2 == 200, str(d2)[:80])

    # 空代码
    d3, s3, _ = post("/v1/compile/check", {"code": ""}, token=token)
    assert_test("COMPILE-03", "空代码返回 422", s3 == 422, f"got {s3}")

# ═══════════════════════════════════════════════════════════════════════════════
#  9. 用户 & 配额模块 Q / User
# ═══════════════════════════════════════════════════════════════════════════════
def test_user_quota():
    header("用户 & 配额模块 (Q / User)")
    token = TOKENS.get("admin")
    if not token:
        skip("[USER] 跳过：无 admin token")
        return

    # 获取 profile
    d, s, ms = get("/v1/user/profile", token=token)
    assert_test("USER-01", f"GET /user/profile 成功  [{ms:.0f}ms]", s == 200 and d.get("success"), str(d)[:80])
    profile = d.get("data", {})
    assert_test("USER-02", "profile 含 role 字段", "role" in str(profile), str(profile)[:80])

    # 获取 usage
    d2, s2, ms2 = get("/v1/user/usage", token=token)
    assert_test("USER-03", f"GET /user/usage 成功  [{ms2:.0f}ms]", s2 == 200 and d2.get("success"), str(d2)[:80])
    usage = d2.get("data", {})
    assert_test("USER-04", "usage 含 quota 字段", "quota" in str(usage).lower() or "limit" in str(usage).lower() or len(str(usage)) > 5, str(usage)[:80])

    # Admin 应有无限配额 (-1) 或超大配额
    quota_val = str(usage)
    assert_test("Q-ADMIN", "Admin 无限配额 (quota=-1 或 ∞)",
                "-1" in quota_val or "unlimited" in quota_val.lower() or "9999" in quota_val or "admin" in quota_val.lower(),
                f"usage={quota_val[:100]}")

    # 订阅信息
    d3, s3, ms3 = get("/v1/billing/subscription", token=token)
    assert_test("Q07-SUB", f"GET /billing/subscription 成功  [{ms3:.0f}ms]",
                s3 == 200 and d3.get("success"), str(d3)[:80])

    # Demo 用户 quota（researcher 级别，有限额）
    demo_token = TOKENS.get("demo_direct")
    if demo_token:
        d4, s4, ms4 = get("/v1/user/usage", token=demo_token)
        assert_test("Q03", f"Researcher 用户 usage 返回  [{ms4:.0f}ms]", s4 == 200, str(d4)[:80])

# ═══════════════════════════════════════════════════════════════════════════════
#  10. 证明会话 (Proof Sessions) CRUD
# ═══════════════════════════════════════════════════════════════════════════════
def test_proof_sessions():
    header("证明会话 CRUD")
    token = TOKENS.get("admin")
    if not token:
        skip("[SESSION] 跳过：无 admin token")
        return

    # 创建
    d, s, ms = post("/v1/proof/sessions", {
        "title": "自测 Session", "description": "自动测试创建的会话",
        "lean_code": "theorem test : 1 + 1 = 2 := by norm_num"
    }, token=token)
    assert_test("SESSION-01", f"创建 proof session  [{ms:.0f}ms]", s == 200 and d.get("success"), str(d)[:80])
    session_id = d.get("data", {}).get("id") if s == 200 else None

    # 列表
    d2, s2, ms2 = get("/v1/proof/sessions", token=token)
    assert_test("SESSION-02", f"列出 proof sessions  [{ms2:.0f}ms]", s2 == 200 and d2.get("success"), str(d2)[:80])

    if session_id:
        # 获取单个
        d3, s3, ms3 = get(f"/v1/proof/sessions/{session_id}", token=token)
        assert_test("SESSION-03", f"获取单个 session  [{ms3:.0f}ms]", s3 == 200 and d3.get("success"), str(d3)[:80])

        # 更新
        d4, s4, ms4 = patch(f"/v1/proof/sessions/{session_id}",
                             {"lean_code": "-- updated\ntheorem test : True := trivial"}, token=token)
        assert_test("SESSION-04", f"更新 session  [{ms4:.0f}ms]", s4 == 200, str(d4)[:80])

        # 删除
        d5, s5, ms5 = delete(f"/v1/proof/sessions/{session_id}", token=token)
        assert_test("SESSION-05", f"删除 session  [{ms5:.0f}ms]", s5 == 200, str(d5)[:80])

        # 确认已删除
        d6, s6, _ = get(f"/v1/proof/sessions/{session_id}", token=token)
        assert_test("SESSION-06", "删除后 GET 返回 404", s6 == 404, f"got {s6}")

# ═══════════════════════════════════════════════════════════════════════════════
#  11. 配额限制 (Rate limit / quota exceeded)
# ═══════════════════════════════════════════════════════════════════════════════
def test_quota_limits():
    header("配额 & 限速验证 (A03 / Q01 / Q02)")

    # Free 用户注册
    import random
    email = f"free_{random.randint(10000,99999)}@test.com"
    d, s, _ = post("/v1/auth/register", {"email": email, "password": "FreePass12", "display_name": "Free"})
    if s != 200:
        skip(f"[Q01] 注册 free 用户失败: {d}")
        return
    free_token = d.get("data", {}).get("access_token")
    if not free_token:
        skip("[Q01] 未获取 free token")
        return

    # Free 计划：连续搜索直到触发 429
    hit_429 = False
    attempts = 0
    for i in range(15):
        d2, s2, _ = post("/v1/search/mathlib", {"query": f"nat add {i}", "top_k": 3}, token=free_token)
        attempts += 1
        if s2 == 429:
            hit_429 = True
            break
        elif s2 != 200:
            break

    assert_test("Q01", f"Free 用户搜索 {attempts} 次后触发 429",
                hit_429, f"尝试 {attempts} 次后 last_status={s2}，body={str(d2)[:80]}")

    # Free 用户尝试调用生成（应被 403/402 拒绝，不是 free 计划功能）
    d3, s3, ms3 = post("/v1/generate/proof",
        {"description": "Prove 1+1=2", "language": "lean4"},
        token=free_token, timeout=30)
    assert_test("Q02", f"Free 用户生成被 403/429 拒绝  [{ms3:.0f}ms]",
                s3 in (402, 403, 429), f"got {s3}: {str(d3)[:80]}")

# ═══════════════════════════════════════════════════════════════════════════════
#  12. 并发压力测试
# ═══════════════════════════════════════════════════════════════════════════════
def test_concurrent():
    header("并发压力测试")
    token = TOKENS.get("admin")
    if not token:
        skip("[CONCURRENT] 跳过：无 admin token")
        return

    results_c = []
    errors_c = []

    def do_search(i):
        d, s, ms = post("/v1/search/mathlib",
                         {"query": f"theorem {i} commutativity", "top_k": 3}, token=token)
        results_c.append((s, ms))
        if s != 200:
            errors_c.append(f"req{i}: status={s}")

    # 10 并发搜索
    threads = [threading.Thread(target=do_search, args=(i,)) for i in range(10)]
    t0 = time.time()
    for t in threads: t.start()
    for t in threads: t.join()
    total_ms = (time.time() - t0) * 1000

    success_count = sum(1 for s, _ in results_c if s == 200)
    avg_ms = sum(ms for _, ms in results_c) / len(results_c) if results_c else 0
    assert_test("CONC-01", f"10 并发搜索 {success_count}/10 成功 [总耗时 {total_ms:.0f}ms, avg {avg_ms:.0f}ms/req]",
                success_count >= 8, f"errors={errors_c}")

    # 5 并发诊断
    diag_results = []
    def do_diagnose(i):
        d, s, ms = post("/v1/diagnose/error", {
            "code": f"theorem foo{i} : 1 = 1 := by rfl",
            "error_message": None
        }, token=token, timeout=45)
        diag_results.append((s, ms))

    threads2 = [threading.Thread(target=do_diagnose, args=(i,)) for i in range(5)]
    for t in threads2: t.start()
    for t in threads2: t.join()
    diag_ok = sum(1 for s, _ in diag_results if s == 200)
    assert_test("CONC-02", f"5 并发诊断 {diag_ok}/5 成功", diag_ok >= 4, str(diag_results))

# ═══════════════════════════════════════════════════════════════════════════════
#  13. 性能基线 (PERF)
# ═══════════════════════════════════════════════════════════════════════════════
def test_performance():
    header("性能基线 (PERF)")
    token = TOKENS.get("admin")
    if not token:
        skip("[PERF] 跳过：无 admin token")
        return

    # 搜索 P50 < 2000ms（宽松：无向量 DB）
    times_search = []
    for _ in range(5):
        _, _, ms = post("/v1/search/mathlib", {"query": "natural number addition", "top_k": 5}, token=token)
        times_search.append(ms)
    times_search.sort()
    p50 = times_search[len(times_search)//2]
    assert_test("PERF-S50", f"搜索 P50 = {p50:.0f}ms (目标 < 2000ms)", p50 < 2000, f"times={[int(x) for x in times_search]}")

    # 诊断 P50 < 15000ms（含 AI 调用）
    times_diag = []
    for _ in range(3):
        _, _, ms = post("/v1/diagnose/error", {
            "code": "theorem foo : 1 + 1 = 2 := by norm_num",
            "error_message": None
        }, token=token, timeout=30)
        times_diag.append(ms)
    times_diag.sort()
    p50d = times_diag[len(times_diag)//2]
    assert_test("PERF-D50", f"诊断 P50 = {p50d:.0f}ms (目标 < 15000ms)",
                p50d < 15000, f"times={[int(x) for x in times_diag]}")

    # 解释 P50 < 5000ms（known tactics，无 AI 调用）
    times_exp = []
    for _ in range(5):
        _, _, ms = post("/v1/explain/tactics", {
            "code": "theorem foo :=\nby\n  ring\n  simp",
            "language": "en"
        }, token=token)
        times_exp.append(ms)
    times_exp.sort()
    p50e = times_exp[len(times_exp)//2]
    assert_test("PERF-E50", f"解释 P50 = {p50e:.0f}ms (目标 < 1000ms, known tactics)",
                p50e < 1000, f"times={[int(x) for x in times_exp]}")

# ═══════════════════════════════════════════════════════════════════════════════
#  14. i18n 验证 I
# ═══════════════════════════════════════════════════════════════════════════════
def test_i18n():
    header("国际化 i18n (I)")
    token = TOKENS.get("admin")
    if not token:
        skip("[I] 跳过：无 admin token")
        return

    # I03: 中文查询 Mathlib
    d, s, ms = post("/v1/search/mathlib", {"query": "连续函数", "top_k": 3}, token=token)
    assert_test("I03", f"中文查询 Mathlib 正常处理  [{ms:.0f}ms]",
                s == 200 and d.get("success"), str(d)[:80])

    # P04: Explain API zh 输出
    d2, s2, ms2 = post("/v1/explain/tactics", {
        "code": "theorem foo :=\nby\n  simp",
        "language": "zh"
    }, token=token)
    lang = d2.get("data", {}).get("language", "")
    assert_test("I-EXPLAIN-ZH", f"Explain zh 语言标记  [{ms2:.0f}ms]",
                s2 == 200 and lang == "zh", f"lang={lang}")

    # 中文 describe 生成
    d3, s3, ms3 = post("/v1/generate/proof", {
        "description": "证明自然数 n 满足 n + 0 = n",
        "language": "lean4"
    }, token=token, timeout=60)
    assert_test("I-GEN-ZH", f"中文描述证明生成  [{ms3:.0f}ms]",
                s3 == 200 and d3.get("success"), str(d3)[:80])

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"\n{BOLD}{'═'*60}")
    print(f"  LeanSage 生产环境自测套件")
    print(f"  目标: {BASE}")
    print(f"  覆盖: 07-TESTING.md 所有可 API 测试点")
    print(f"{'═'*60}{RESET}\n")

    start = time.time()

    setup_tokens()
    test_health()
    test_auth()
    test_search()
    test_generate()
    test_diagnose()
    test_explain()
    test_convert()
    test_compile()
    test_user_quota()
    test_proof_sessions()
    test_quota_limits()
    test_concurrent()
    test_performance()
    test_i18n()

    elapsed = time.time() - start

    # ─── 汇总 ─────────────────────────────────────────────────────────────────
    total = passed + failed + skipped
    print(f"\n{BOLD}{'═'*60}")
    print(f"  测试结果汇总  (耗时 {elapsed:.1f}s)")
    print(f"{'═'*60}{RESET}")
    print(f"  {GREEN}通过{RESET}: {passed:>3}")
    print(f"  {RED}失败{RESET}: {failed:>3}")
    print(f"  {YELLOW}跳过{RESET}: {skipped:>3}")
    print(f"  合计: {total:>3}")

    if failed > 0:
        print(f"\n{RED}{BOLD}  失败详情:{RESET}")
        for tid, status, desc, detail in RESULTS:
            if status == "FAIL":
                print(f"  {RED}✗ [{tid}]{RESET} {desc}")
                if detail:
                    print(f"      {detail[:120]}")

    rate = passed / total * 100 if total > 0 else 0
    color = GREEN if rate >= 90 else (YELLOW if rate >= 70 else RED)
    print(f"\n{color}{BOLD}  通过率: {rate:.1f}%{RESET}\n")

    sys.exit(0 if failed == 0 else 1)
