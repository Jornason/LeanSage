# LeanSage 自动化测试套件

## 目录结构

```
dev/test/
├── conftest.py              # 共享 fixtures（HTTP client、token、free_user）
├── pytest.ini               # pytest 配置（marks、timeout、testpaths）
├── requirements.txt         # 测试依赖（httpx、pytest、pytest-timeout、pytest-xdist）
├── .env.test.example        # 环境变量模板（复制为 .env.test 后填写）
├── run_tests.sh             # 一键运行脚本（支持多种模式）
│
├── smoke/                   # 快速冒烟测试（< 10s，无 AI 调用）
│   └── test_smoke.py        # 健康检查 + 核心路径验证（15 个测试）
│
└── api/                     # API 集成测试（按模块分文件）
    ├── test_health.py        # 健康检查（5 个）
    ├── test_auth.py          # 认证与安全（13 个）
    ├── test_search.py        # Mathlib 搜索（11 个）
    ├── test_generate.py      # 证明生成（12 个，含 AI）
    ├── test_diagnose.py      # 错误诊断（10 个，含 AI）
    ├── test_explain.py       # Tactic 解释（12 个）
    ├── test_convert.py       # LaTeX 转换（8 个）
    ├── test_compile.py       # 编译检查（6 个）
    ├── test_user.py          # 用户 & 配额（9 个）
    ├── test_sessions.py      # 证明会话 CRUD（8 个）
    ├── test_billing.py       # 计费 & 订阅（8 个）
    ├── test_quota.py         # 限速 & 配额（6 个）
    └── test_concurrent.py    # 并发压力（3 个）
```

---

## 快速开始

### 1. 安装依赖

```bash
cd dev/test
pip install -r requirements.txt
```

### 2. 运行冒烟测试（最快，约 10s，不调用 AI）

```bash
bash run_tests.sh --smoke
```

### 3. 完整回归测试（本地服务器）

```bash
bash run_tests.sh
```

### 4. 完整回归测试（生产服务器）

```bash
bash run_tests.sh --target PROD
```

---

## 运行模式

| 命令 | 说明 | 耗时参考 |
|------|------|----------|
| `bash run_tests.sh --smoke` | 冒烟（无 AI） | ~10s |
| `bash run_tests.sh --no-ai` | 全量跳过 AI 测试 | ~30s |
| `bash run_tests.sh` | 完整回归 | ~3–5min |
| `bash run_tests.sh --parallel` | 4 worker 并行 | ~1–2min |
| `bash run_tests.sh --mark search` | 只跑搜索模块 | ~5s |
| `bash run_tests.sh --mark "auth or quota"` | 组合 mark | ~15s |
| `bash run_tests.sh --target PROD` | 针对生产环境 | 同上 |

### pytest 直接运行（更灵活）

```bash
cd dev/test

# 只跑某个文件
pytest api/test_auth.py -v

# 只跑某个 mark
pytest -m smoke -v
pytest -m "generate and ai" -v
pytest -m "not ai" -v

# 只跑关键字匹配的测试
pytest -k "quota" -v
pytest -k "concurrent" -v

# 指定目标服务器
BASE_URL=http://47.242.43.35:9019 pytest -m smoke -v
```

---

## 环境变量

复制 `.env.test.example` 为 `.env.test` 并按需修改：

```bash
cp .env.test.example .env.test
```

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `BASE_URL` | `http://localhost:9019` | 目标服务器 |
| `ADMIN_EMAIL` | `admin@leanprove.ai` | Admin 账号 |
| `ADMIN_PASSWORD` | `admin12345` | Admin 密码 |
| `DEMO_EMAIL` | `demo@leanprove.ai` | Demo 账号 |
| `DEMO_PASSWORD` | `demo12345` | Demo 密码 |

---

## Pytest Marks 说明

| Mark | 含义 | 是否含 AI |
|------|------|----------|
| `smoke` | 冒烟测试，快速验证核心路径 | 否 |
| `auth` | 认证 & 安全 | 否 |
| `search` | Mathlib 搜索 | 否 |
| `generate` | 证明生成 | 是 |
| `diagnose` | 错误诊断 | 是 |
| `explain` | Tactic 解释 | 部分 |
| `convert` | LaTeX 转换 | 否 |
| `compile` | 编译检查 | 否 |
| `user` | 用户 & 配额 | 否 |
| `sessions` | 证明会话 CRUD | 否 |
| `billing` | 计费 & 订阅 | 否 |
| `quota` | 限速 & 配额 | 否 |
| `concurrent` | 并发压力 | 部分 |
| `ai` | 调用 aws-gpt-5.4 的测试 | 是 |
| `slow` | 单个测试 > 30s | 是 |

跳过所有 AI 测试：`pytest -m "not ai"`

---

## CI/CD 集成示例

### GitHub Actions

```yaml
- name: Run smoke tests
  run: |
    pip install -r dev/test/requirements.txt
    cd dev/test
    BASE_URL=http://localhost:9019 pytest -m smoke -v

- name: Run full regression (nightly)
  run: |
    cd dev/test
    BASE_URL=${{ secrets.PROD_URL }} bash run_tests.sh --no-ai
```

### 每次部署后自测

```bash
# 上传并在服务器上运行冒烟测试
rsync -avz dev/test/ root@47.242.43.35:~/leansage/test/
ssh root@47.242.43.35 "cd ~/leansage/test && pip install -q -r requirements.txt && BASE_URL=http://localhost:9019 pytest -m smoke -v"
```

---

## 覆盖范围（对应 07-TESTING.md）

| 测试点 | 覆盖状态 |
|--------|---------|
| S01–S07 搜索 | ✅ 全覆盖 |
| G01–G03 生成 | ✅ 覆盖（G04/G05 功能未实现） |
| D01–D03, D05b 诊断 | ✅ 覆盖 |
| P01–P06, P08 解释 | ✅ 全覆盖 |
| X01, X02, X05, X09, X10 转换 | ✅ 覆盖 |
| A02, A03, AU01–AU05 认证 | ✅ 全覆盖 |
| Q01–Q03, Q07 配额计费 | ✅ 覆盖 |
| SESSION CRUD | ✅ 全覆盖 |
| CONC-01, CONC-02 并发 | ✅ 覆盖 |
| I03 国际化（API 层） | ✅ 覆盖 |
| E/L 系列（编辑器/LSP） | ⚡ 需浏览器 E2E（Playwright） |
