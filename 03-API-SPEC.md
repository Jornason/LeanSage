# API 接口规范 - LeanProve AI

## 项目信息

| 字段 | 内容 |
|------|------|
| 项目名称 | LeanProve AI |
| API 版本 | v1 |
| Base URL | `https://api.leanprove.ai/v1` |

---

## 1. 通用约定

### 请求格式
- Content-Type: `application/json`
- 认证: `Authorization: Bearer <jwt_token>`
- 请求 ID: 自动分配 `X-Request-Id`

### 标准响应

```json
{"success": true, "data": {}, "meta": {"request_id": "req_abc123", "timestamp": "2026-03-06T12:00:00Z"}}
```

### 错误码表

| HTTP | 错误码 | 描述 |
|------|--------|------|
| 400 | INVALID_INPUT | 请求参数无效 |
| 401 | UNAUTHORIZED | 未认证或 Token 过期 |
| 403 | FORBIDDEN | 无权访问 |
| 404 | NOT_FOUND | 资源不存在 |
| 422 | VALIDATION_ERROR | 输入验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 超出配额限制 |
| 500 | INTERNAL_ERROR | 服务器内部错误 |
| 502 | UPSTREAM_ERROR | Claude/Modal 不可用 |

### 分页
查询参数: `page` (默认1), `per_page` (默认20, 最大100)。响应含 `pagination` 对象。

---

## 2. 核心接口

### 2.1 Mathlib 语义搜索

**POST** `/search/mathlib` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| query | string | 是 | 自然语言查询，1-500 字符 |
| top_k | integer | 否 | 返回数量，默认 5，最大 20 |
| filter_module | string | 否 | 限定模块如 "Topology" |

**请求**:
```json
{"query": "连续函数的和仍然是连续函数", "top_k": 5}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "rank": 1,
        "theorem_name": "Continuous.add",
        "full_name": "Mathlib.Topology.ContinuousOn.add",
        "type_signature": "theorem Continuous.add {f g : α → β} [TopologicalSpace α] [TopologicalSpace β] [Add β] [ContinuousAdd β] (hf : Continuous f) (hg : Continuous g) : Continuous (fun x => f x + g x)",
        "module": "Mathlib.Topology.Algebra.Group.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/Group/Basic.html",
        "similarity": 0.934
      },
      {
        "rank": 2,
        "theorem_name": "ContinuousOn.add",
        "full_name": "Mathlib.Topology.ContinuousOn.add",
        "type_signature": "theorem ContinuousOn.add {f g : α → β} {s : Set α} (hf : ContinuousOn f s) (hg : ContinuousOn g s) : ContinuousOn (fun x => f x + g x) s",
        "module": "Mathlib.Topology.Algebra.Group.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/...",
        "similarity": 0.891
      }
    ],
    "query_embedding_time_ms": 120,
    "search_time_ms": 45
  }
}
```

**业务规则**: Free 用户 10 次/月；Researcher 无限；结果缓存 1 小时。

---

### 2.2 证明草稿生成

**POST** `/generate/proof` | 认证: Bearer Token (Researcher+)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| description | string | 是 | 自然语言定理描述，1-2000 字符 |
| context | string | 否 | 额外上下文（已有 import 等） |
| style | string | 否 | "tactic"(默认) / "term" |
| auto_compile | boolean | 否 | 是否自动编译检查，默认 true |

**请求**:
```json
{
  "description": "证明：对于所有自然数 n，n + 0 = n",
  "style": "tactic",
  "auto_compile": true
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "lean_code": "import Mathlib.Tactic\n\ntheorem add_zero_eq (n : ℕ) : n + 0 = n := by\n  simp",
    "compilation": {
      "status": "success",
      "errors": [],
      "time_ms": 3200
    },
    "used_lemmas": ["Nat.add_zero"],
    "explanation": "此证明使用 simp tactic 自动化简，底层调用了 Nat.add_zero 引理。",
    "generation_time_ms": 2800
  }
}
```

**业务规则**: 编译超时 60s；自动重试最多 3 次；单次消耗 1 额度。

---

### 2.3 证明错误诊断

**POST** `/diagnose/error` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| code | string | 是 | Lean 4 源代码，最大 10000 字符 |
| error_message | string | 否 | 编译器错误信息（可选，服务端可自动编译） |

**请求**:
```json
{
  "code": "theorem bad_proof (n : Nat) : n + 1 > n := by\n  omega_bad",
  "error_message": "unknown tactic 'omega_bad'"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "diagnostics": [
      {
        "line": 2,
        "column": 2,
        "severity": "error",
        "original_error": "unknown tactic 'omega_bad'",
        "explanation": "Lean 4 中没有名为 'omega_bad' 的 tactic。你可能想使用 'omega' tactic，它可以自动求解线性算术目标。",
        "suggestions": [
          {
            "description": "将 omega_bad 替换为 omega",
            "fixed_code": "theorem bad_proof (n : Nat) : n + 1 > n := by\n  omega",
            "confidence": 0.95
          }
        ]
      }
    ]
  }
}
```

**业务规则**: Free 用户 10 次/月共享配额；诊断含自动编译。

---

### 2.4 LaTeX → Lean 转换

**POST** `/convert/latex-to-lean` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| latex | string | 是 | LaTeX 数学表达式 |
| include_imports | boolean | 否 | 是否包含 import 语句，默认 false |

**请求**:
```json
{"latex": "\\forall \\epsilon > 0, \\exists N \\in \\mathbb{N}, \\forall n \\geq N, |a_n - L| < \\epsilon"}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "lean_expression": "∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε",
    "lean_declaration": "def seq_limit (a : ℕ → ℝ) (L : ℝ) : Prop :=\n  ∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε",
    "imports": ["import Mathlib.Analysis.SpecificLimits.Basic"]
  }
}
```

**业务规则**: 支持常见 LaTeX 宏；不支持自定义宏。

---

### 2.5 Lean → LaTeX 转换

**POST** `/convert/lean-to-latex` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| lean_code | string | 是 | Lean 4 表达式或声明 |
| format | string | 否 | "inline" / "display"(默认) |

**请求**:
```json
{"lean_code": "∀ ε > 0, ∃ N : ℕ, ∀ n ≥ N, |a n - L| < ε", "format": "display"}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "latex": "\\forall \\epsilon > 0,\\ \\exists N \\in \\mathbb{N},\\ \\forall n \\geq N,\\ |a_n - L| < \\epsilon",
    "rendered_preview_url": "https://api.leanprove.ai/v1/render/katex?expr=..."
  }
}
```

---

### 2.6 Lean 编译检查

**POST** `/compile/check` | 认证: Bearer Token (Researcher+)

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| code | string | 是 | Lean 4 完整源代码 |
| timeout_seconds | integer | 否 | 超时秒数，默认 60，最大 120 |

**请求**:
```json
{"code": "import Mathlib.Tactic\n\ntheorem test : 1 + 1 = 2 := by norm_num"}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "status": "success",
    "errors": [],
    "warnings": [],
    "goals": [],
    "time_ms": 4500,
    "lean_version": "4.8.0",
    "mathlib_version": "2026-03-01"
  }
}
```

**业务规则**: Modal.com 冷启动约 30s，热实例 < 5s；超时返回 408。

---

### 2.7 证明步骤解释

**POST** `/explain/tactics` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| code | string | 是 | 含 tactic 的 Lean 4 证明 |
| language | string | 否 | 解释语言 "zh"/"en"，默认 "en" |

**请求**:
```json
{
  "code": "theorem add_comm (a b : ℕ) : a + b = b + a := by\n  induction a with\n  | zero => simp\n  | succ n ih => simp [Nat.succ_add, ih]",
  "language": "zh"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "steps": [
      {"tactic": "induction a with", "explanation": "对自然数 a 进行归纳：分基础情形 (a=0) 和归纳步骤 (a=n+1) 两种情况讨论。"},
      {"tactic": "| zero => simp", "explanation": "基础情形：当 a=0 时，需证 0+b = b+0。simp 自动化简完成。"},
      {"tactic": "| succ n ih => simp [Nat.succ_add, ih]", "explanation": "归纳步骤：假设 n+b=b+n (归纳假设 ih)，需证 (n+1)+b = b+(n+1)。使用 Nat.succ_add 展开后代入归纳假设完成。"}
    ]
  }
}
```

---

### 2.8 用户用量查询

**GET** `/user/usage` | 认证: Bearer Token

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| period | string | 否 | "current_month"(默认) / "last_month" / "all" |

**请求**: `GET /v1/user/usage?period=current_month`

**响应**:
```json
{
  "success": true,
  "data": {
    "plan": "researcher",
    "period": "2026-03",
    "searches": {"used": 47, "limit": -1},
    "generations": {"used": 12, "limit": -1},
    "diagnoses": {"used": 8, "limit": -1},
    "compilations": {"used": 23, "limit": -1},
    "api_calls_today": 15,
    "rate_limit": {"requests_per_minute": 30, "remaining": 28}
  }
}
```

---

## 3. WebSocket 接口

### 3.1 实时编译状态

**WS** `wss://api.leanprove.ai/v1/ws/compile`

连接后发送 Lean 代码，服务端流式返回编译进度和诊断信息。

**客户端消息**:
```json
{"type": "code_update", "code": "import Mathlib.Tactic\n...", "cursor_line": 5}
```

**服务端消息**:
```json
{"type": "status", "status": "compiling", "progress": 0.3}
{"type": "diagnostic", "line": 5, "severity": "error", "message": "type mismatch..."}
{"type": "status", "status": "done", "time_ms": 4200}
{"type": "goal", "line": 5, "goal": "⊢ a + b = b + a"}
```

**心跳**: 客户端每 30s 发送 `{"type": "ping"}`，服务端回复 `{"type": "pong"}`。

---

## 4. 第三方接口集成

| 服务 | 用途 | 接口 | 认证方式 |
|------|------|------|----------|
| Claude API (Anthropic) | 证明生成/诊断/解释 | `POST /v1/messages` | API Key Header |
| OpenAI Embeddings | 文本向量化 | `POST /v1/embeddings` | API Key Header |
| Modal.com | Lean 编译执行 | Python SDK `@modal.function` | Token Auth |
| Supabase Auth | 用户认证 | REST + GoTrue | Service Role Key |
| Stripe | 订阅计费 | REST API v2024-12 | Secret Key |
| GitHub OAuth | 社交登录 | OAuth 2.0 流程 | Client ID/Secret |