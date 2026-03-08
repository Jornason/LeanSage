# 实施计划 - LeanProve AI

## 1. 里程碑

| 里程碑 | 目标 | 开始 | 结束 |
|--------|------|------|------|
| M1 | 基础架构+认证+Mathlib索引 | 03-10 | 03-31 |
| M2 | 搜索+生成+诊断 MVP | 04-01 | 04-30 |
| M3 | 编辑器+LSP+转换 | 05-01 | 05-31 |
| M4 | 计费+机构License+上线 | 06-01 | 06-30 |

## 2. 任务拆分

### M1 基础架构
- [ ] T01 初始化 Next.js 14 + Tailwind + 基础布局
- [ ] T02 配置 CodeMirror 6 + Lean 4 语法高亮
- [ ] T03 集成 KaTeX 公式渲染
- [ ] T04 初始化 FastAPI 项目 + Pydantic schemas
- [ ] T05 Supabase 数据库迁移脚本(7张表)
- [ ] T06 Supabase Auth (GitHub OAuth + 邮箱)
- [ ] T07 JWT 中间件 + RBAC 装饰器
- [ ] T08 Mathlib 定理抽取脚本(解析 .lean)
- [ ] T09 Embedding 批量向量化 pipeline(20万条)
- [ ] T10 Chroma 向量库初始化+持久化

### M2 核心功能
- [ ] T11 SearchService 向量检索+Claude rerank
- [ ] T12 搜索 API 端点+验证+缓存
- [ ] T13 搜索前端页面(输入+结果卡片+KaTeX)
- [ ] T14 GenerationService Prompt工程+Claude生成
- [ ] T15 Modal.com Lean 编译函数
- [ ] T16 生成 API 端点+自动编译重试
- [ ] T17 证明工作台前端(三栏布局)
- [ ] T18 DiagnosisService 错误分析+修复建议
- [ ] T19 诊断 API 端点+前端页面
- [ ] T20 Rate limiting (令牌桶+Redis)

### M3 增强体验
- [ ] T21 WebSocket 编译状态推送
- [ ] T22 Lean LSP 集成(Modal实例)
- [ ] T23 编辑器实时诊断+目标显示
- [ ] T24 LaTeX→Lean 转换 API+前端
- [ ] T25 Lean→LaTeX 转换 API+前端
- [ ] T26 Tactic 步骤解释 API+面板
- [ ] T27 证明会话自动保存+历史版本

### M4 商业化
- [ ] T28 Stripe 集成(3档订阅)
- [ ] T29 用量统计仪表盘
- [ ] T30 机构 License 管理后台
- [ ] T31 Landing Page + SEO
- [ ] T32 E2E 测试 + 性能优化
- [ ] T33 部署流水线(Vercel+Modal)
- [ ] T34 文档站 + API 文档

## 3. 关键任务详情

### T09 Embedding 批量向量化

| 字段 | 内容 |
|------|------|
| 优先级 | P0 |
| 工时 | 3天 |
| 前置 | T08 Mathlib 定理抽取 |
| AI协同 | Claude 辅助编写抽取脚本；Cursor 调试 |

**步骤**:
1. 从 Mathlib4 源码抽取所有 theorem/lemma 的 name + type_signature + docstring
2. 拼接文本: `"{short_name}: {type_signature}. {docstring}"`
3. 调用 OpenAI text-embedding-3-small 批量 API（每批 2048 条）
4. 写入 Chroma collection，设置 `metadata` 含 module_path
5. 同步写入 PostgreSQL mathlib_theorems 表（备份+元数据查询）
6. 验证: 随机抽样 100 条查询，检查 Top-5 召回率

**验收**: 20 万条全部入库；抽样 Top-5 召回率 >= 75%；总耗时 < 4 小时

### T14 GenerationService

| 字段 | 内容 |
|------|------|
| 优先级 | P0 |
| 工时 | 5天 |
| 前置 | T11 SearchService |
| AI协同 | Claude 生成 Prompt 模板；Claude 自身作为推理引擎 |

**步骤**:
1. 设计 System Prompt: 包含 Lean 4 语法规范 + Mathlib 常用 import
2. 实现 RAG 流程: 自然语言 → SearchService 检索相关引理 → 构建上下文
3. 调用 Claude API 生成证明代码
4. Modal.com 编译检查；失败则将错误反馈给 Claude 重试（最多 3 次）
5. 返回最终代码 + 使用引理列表 + 自然语言解释

**验收**: 100 个测试用例编译通过率 >= 40%；平均响应 < 15s

### T15 Modal.com Lean 编译函数

| 字段 | 内容 |
|------|------|
| 优先级 | P0 |
| 工时 | 3天 |
| 前置 | T04 FastAPI 项目 |
| AI协同 | Claude 编写 Modal 函数模板 |

**步骤**:
1. 创建 Modal App + Lean 4 Docker 镜像（含 mathlib4 缓存）
2. 编写 `@modal.function` 接受 Lean 代码 → 写入临时文件 → `lake build` → 收集输出
3. 实现超时控制（60s）和沙箱隔离
4. 添加预热池（保持 2 个 warm 实例减少冷启动）
5. 集成到 FastAPI 后端，异步调用

**验收**: 热启动 < 5s；冷启动 < 35s；并发 10 编译无冲突

### T11 SearchService

| 字段 | 内容 |
|------|------|
| 优先级 | P0 |
| 工时 | 3天 |
| 前置 | T09 T10 |
| AI协同 | Claude 辅助 rerank 提示词设计 |

**步骤**:
1. 接收自然语言查询 → OpenAI embedding 向量化
2. Chroma 相似度检索 Top-20
3. Claude rerank: 将 20 条结果 + 原始查询发给 Claude，返回排序后 Top-5
4. Redis 缓存结果（key=query_hash, TTL=1h）
5. 记录 search_logs

**验收**: Top-5 召回率 >= 75%；P95 延迟 < 2s；缓存命中率 > 30%

### T28 Stripe 集成

| 字段 | 内容 |
|------|------|
| 优先级 | P0 |
| 工时 | 4天 |
| 前置 | T06 Auth |
| AI协同 | Cursor 生成 Stripe webhook handler |

**步骤**:
1. Stripe Dashboard 创建 3 个 Price（Free/Researcher/Lab）
2. 实现 Checkout Session 创建 API
3. 实现 Customer Portal 链接生成
4. Webhook handler: invoice.paid → 更新 subscription 状态
5. Webhook handler: customer.subscription.deleted → 降级为 free
6. 前端定价页面 + Checkout 跳转

**验收**: 订阅/升级/降级/取消全流程通过；Webhook 幂等处理

## 4. 技术风险

| 风险 | 影响 | 概率 | 缓解措施 |
|------|------|------|----------|
| Lean 编译冷启动慢(30s+) | 用户体验差 | 高 | Modal 预热池；编译结果缓存；提示用户等待 |
| Claude 证明生成质量不稳定 | 编译通过率低 | 中 | 多轮重试；RAG 提供更多上下文；收集反馈微调 Prompt |
| Mathlib 频繁更新导致索引失效 | 搜索结果过期 | 中 | 每周自动重建索引；双写原子切换 |
| Chroma 在 20 万条规模性能瓶颈 | 搜索延迟高 | 低 | 预留迁移至 Pinecone/Weaviate 方案；分片策略 |
| Claude API 成本超预算 | 亏损 | 中 | 严格 rate limit；缓存重复查询；监控每用户成本 |

## 5. AI 协同计划

| 环节 | AI 工具 | 用途 | 预期提效 |
|------|---------|------|----------|
| 代码编写 | Cursor + Claude | 生成 boilerplate、API handler、测试 | 50% |
| Prompt 工程 | Claude Console | 迭代证明生成/诊断 System Prompt | 核心竞争力 |
| 文档撰写 | Claude | API 文档、用户指南 | 60% |
| 代码审查 | Claude Code Review | PR 审查、安全扫描 | 40% |
| 测试生成 | Cursor | 单元测试、边界用例 | 50% |
| Mathlib 解析 | Claude | 理解复杂类型签名、生成描述文本 | 70% |
