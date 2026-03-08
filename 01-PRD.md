# 产品需求文档 (PRD) - LeanProve AI

## 项目信息

| 字段 | 内容 |
|------|------|
| 项目名称 | LeanProve AI |
| 版本 | v0.1.0 |
| 负责人 | TBD |
| 创建日期 | 2026-03-06 |
| 目标上线 | 2026-06-01 |
| 状态 | 规划中 |

---

## 1. 背景与目标

### 1.1 问题描述

形式化证明（Lean 4 / Coq / Isabelle）学习曲线极陡。Mathlib 库含 20 万+ 定理，研究者难以快速定位所需引理。Lean 4 编译错误信息晦涩，初学者需数小时调试简单 tactic 错误。LaTeX 论文与 Lean 代码之间缺乏自动转换工具，导致形式化验证工作重复且低效。

### 1.2 目标用户

| 用户群体 | 规模 | 核心痛点 |
|----------|------|----------|
| 高校数学系研究生 | ~3万 | Lean 入门困难，找不到合适引理 |
| 形式化验证研究员 | ~5千 | Mathlib 检索效率低，证明调试耗时 |
| 数学教授/讲师 | ~2千 | 需要教学辅助工具演示证明过程 |
| 定理证明爱好者 | ~2万 | 缺乏在线可用的 Lean 环境 |
| 企业验证团队 | ~500 | 需要批量授权 + 私有部署 |

### 1.3 项目目标

1. 提供 Mathlib 全量定理语义搜索，Top-5 召回率 ≥ 80%
2. 实现自然语言→Lean 4 证明草稿自动生成，编译通过率 ≥ 40%
3. 证明错误诊断准确率 ≥ 70%，平均响应时间 < 5 秒
4. 上线 6 个月内获取 5,000 注册用户，500 付费用户
5. 建立高校合作关系 ≥ 3 所，获取机构 License 客户 ≥ 2 家

### 1.4 成功指标

| 指标 | 基线 | 目标(3个月) | 目标(6个月) |
|------|------|-------------|-------------|
| 注册用户数 | 0 | 2,000 | 5,000 |
| MAU | 0 | 800 | 2,500 |
| 付费转化率 | 0% | 8% | 10% |
| 搜索 Top-5 召回率 | N/A | 75% | 80% |
| 证明生成编译通过率 | N/A | 35% | 45% |
| MRR | $0 | $5,000 | $15,000 |

---

## 2. 功能需求

### 2.1 P0 - 核心功能

| 编号 | 功能 | 描述 | 验收标准 |
|------|------|------|----------|
| P0-1 | Mathlib 语义搜索 | 用户输入自然语言描述，返回 Top-K 相关 Mathlib 定理 | 输入"连续函数的和是连续的"→返回含 `Continuous.add` 的结果；延迟 < 2s |
| P0-2 | 证明草稿生成 | 用户描述定理 → Claude 生成 Lean 4 证明框架 | 生成代码含 `theorem` 声明 + sorry 占位或完整 tactic；编译通过率 ≥ 40% |
| P0-3 | 证明错误诊断 | 粘贴报错 Lean 代码 → AI 解释错误原因 + 修复建议 | 返回错误位置标注 + 自然语言解释 + 至少 1 条修复建议 |
| P0-4 | 用户认证系统 | GitHub OAuth + 邮箱注册 | 支持 GitHub SSO；邮箱验证；JWT Token 管理 |
| P0-5 | 订阅计费 | Free/Researcher/Lab 三档 + Stripe 集成 | 用量按月重置；超额提示升级；Stripe Webhook 处理 |
| P0-6 | 代码编辑器 | CodeMirror 集成 Lean 4 语法高亮 | 支持 Lean 4 关键字高亮、括号匹配、行号 |

### 2.2 P1 - 重要功能

| 编号 | 功能 | 描述 | 验收标准 |
|------|------|------|----------|
| P1-1 | 实时 Lean 编译检查 | 在线编辑器接入 Lean LSP，实时显示编译状态 | 编辑器底栏显示 ✓/✗；错误红色波浪线标注；延迟 < 10s |
| P1-2 | LaTeX↔Lean 转换 | LaTeX 数学表达式 ↔ Lean 4 类型签名双向转换 | `\forall x, f(x) > 0` → `∀ x, f x > 0`；反向同理 |
| P1-3 | 证明步骤解释 | Lean 4 tactic 序列翻译成自然语言数学描述 | 输入 `simp [add_comm]` → 输出"利用加法交换律化简" |

### 2.3 P2 - 增值功能

| 编号 | 功能 | 描述 | 验收标准 |
|------|------|------|----------|
| P2-1 | 机构 License | 高校/企业批量授权管理后台 | 管理员可添加/移除席位；用量汇总报表；SSO 集成 |
| P2-2 | 证明协作 | 多人实时协作编辑同一证明 | WebSocket 实时同步；光标位置共享；冲突解决 |

---

## 3. 非功能需求

| 类别 | 要求 |
|------|------|
| 性能 | API P95 延迟 < 3s（搜索）、< 15s（证明生成）；并发 500 用户 |
| 可用性 | SLA 99.5%；计划维护提前 24h 通知 |
| 安全 | 用户代码端到端加密存储；GDPR 合规；SOC2 Type I（12个月内） |
| 可扩展性 | 水平扩展至 10 万用户无需重构 |
| 国际化 | 支持中/英文 UI；定理描述支持多语言输入 |

---

## 4. 约束条件

- Lean 4 编译需要专用环境（Modal.com GPU 实例），冷启动约 30s
- Mathlib 定理库更新频繁（约每周），embedding 需定期重建
- Claude API 调用成本约 $0.003/次搜索、$0.015/次证明生成
- 目标用户群体小众但高价值，获客需依赖学术社区口碑

---

## 5. 用户故事

### US-1: 研究生查找引理

**作为**一名数学系研究生，**我想**用自然语言搜索"实数序列的极限唯一性"，**以便**快速找到 Mathlib 中对应的定理名称和类型签名，而不用手动翻阅文档。

**验收条件**：
- 输入中文/英文描述均可返回结果
- 结果包含定理全名（如 `tendsto_nhds_unique`）、类型签名、所在文件路径
- 点击结果跳转 Mathlib 文档页面
- 搜索延迟 < 2 秒

### US-2: 教授生成教学证明

**作为**一名数学教授，**我想**输入"证明：如果 f 和 g 都是连续函数，那么 f+g 也是连续函数"，**以便**获得一个可编译的 Lean 4 证明框架，用于课堂演示。

**验收条件**：
- 生成的代码包含正确的 `import` 语句
- 定理声明与自然语言描述语义一致
- 证明体使用合理的 tactic（如 `exact Continuous.add hf hg`）
- 提供"一键复制"按钮

### US-3: 初学者调试证明错误

**作为**一名 Lean 4 初学者，**我想**粘贴一段有编译错误的证明代码，**以便**获得通俗易懂的错误解释和修复建议。

**验收条件**：
- 错误位置在代码中高亮标注
- 解释使用中文/英文（根据用户偏好）
- 修复建议可一键应用到编辑器
- 支持多个错误同时诊断

---

## 6. 概念图提示词

```
Create a product concept diagram for "LeanProve AI", a math research AI assistant.
Layout: center is the main platform logo. Top section shows 3 user personas
(graduate student, professor, researcher) with arrows pointing to the platform.
Middle section shows 4 core features as cards: "Mathlib Semantic Search" with a
magnifying glass icon, "Proof Generation" with a magic wand icon, "Error Diagnosis"
with a bug icon, "LaTeX↔Lean Converter" with a bidirectional arrow icon.
Bottom section shows the tech stack: Claude API, Lean 4 LSP, Chroma Vector DB,
Supabase. Right side shows pricing tiers stacked vertically.
Style: clean, academic, blue-purple gradient theme, mathematical symbols scattered
as decorative elements. Nano Banana Pro format, 1920x1080.
```


![prd_01](images/prd_01.png)
