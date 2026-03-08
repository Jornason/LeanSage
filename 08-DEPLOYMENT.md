# 部署文档 - LeanProve AI

## 1. 环境配置

| 环境 | 用途 | URL | 基础设施 |
|------|------|-----|----------|
| Development | 本地开发 | localhost:3000/8000 | 本地Docker |
| Staging | 预发布测试 | staging.leanprove.ai | Vercel Preview + Modal staging |
| Production | 生产 | leanprove.ai | Vercel + Modal + Supabase |

## 2. 部署流程

### 前端 (Vercel)
1. PR 合并到 `main` 分支
2. Vercel 自动触发构建 (`next build`)
3. 构建产物部署到 Edge Network
4. Vercel Preview 自动为每个 PR 生成预览 URL
5. 生产部署需手动 Promote 或自动（main 分支）

### 后端 (Railway / Fly.io)
1. PR 合并到 `main` 分支
2. CI 运行测试套件 (pytest)
3. 构建 Docker 镜像 → 推送到 Registry
4. Railway 自动部署新版本（滚动更新）
5. 健康检查通过后切换流量

### Lean 编译服务 (Modal.com)
1. `modal deploy lean_compiler.py`
2. Modal 自动构建镜像（含 Lean 4 + mathlib4 缓存）
3. 部署无服务器函数
4. 预热 2 个 warm 实例

### 数据库 (Supabase)
1. 编写迁移脚本 `supabase migration new <name>`
2. 本地测试 `supabase db reset`
3. 推送到 staging `supabase db push --linked`
4. 生产推送 `supabase db push`

## 3. 环境变量

| 变量 | 描述 | 示例 | 必填 |
|------|------|------|------|
| NEXT_PUBLIC_SUPABASE_URL | Supabase项目URL | https://xxx.supabase.co | 是 |
| NEXT_PUBLIC_SUPABASE_ANON_KEY | Supabase匿名Key | eyJhb... | 是 |
| SUPABASE_SERVICE_ROLE_KEY | Supabase服务端Key | eyJhb... | 是 |
| ANTHROPIC_API_KEY | Claude API密钥 | sk-ant-... | 是 |
| OPENAI_API_KEY | OpenAI Embedding密钥 | sk-... | 是 |
| MODAL_TOKEN_ID | Modal认证ID | ak-... | 是 |
| MODAL_TOKEN_SECRET | Modal认证Secret | as-... | 是 |
| STRIPE_SECRET_KEY | Stripe密钥 | sk_live_... | 是 |
| STRIPE_WEBHOOK_SECRET | Stripe Webhook签名 | whsec_... | 是 |
| STRIPE_PRICE_RESEARCHER | Researcher价格ID | price_... | 是 |
| STRIPE_PRICE_LAB | Lab价格ID | price_... | 是 |
| UPSTASH_REDIS_URL | Redis连接URL | rediss://... | 是 |
| UPSTASH_REDIS_TOKEN | Redis Token | AX... | 是 |
| CHROMA_HOST | Chroma地址 | http://chroma:8000 | 是 |
| DATABASE_URL | PostgreSQL连接串 | postgresql://... | 是 |
| JWT_SECRET | JWT签名密钥 | random-32-bytes | 是 |
| SENTRY_DSN | Sentry错误追踪 | https://...@sentry.io/... | 否 |
| POSTHOG_KEY | PostHog分析Key | phc_... | 否 |

## 4. 监控告警

| 指标 | 阈值 | 告警渠道 | 处理方式 |
|------|------|----------|----------|
| API错误率 | > 5% (5min) | Slack + PagerDuty | 检查日志;必要时回滚 |
| API P95延迟 | > 10s | Slack | 检查下游依赖 |
| Claude API失败率 | > 2% | Slack | 启用缓存降级 |
| Modal冷启动率 | > 50% | Slack | 增加预热实例 |
| 磁盘使用 | > 80% | Email | 清理日志/扩容 |
| Supabase连接池 | > 80% | Slack | 扩大连接池 |
| 月度API成本 | > $2000 | Email | 审查用量;优化缓存 |

## 5. 回滚方案

| 组件 | 回滚方式 | 耗时 |
|------|----------|------|
| 前端 (Vercel) | Vercel Dashboard → Deployments → Rollback | < 1min |
| 后端 (Railway) | Railway Dashboard → Rollback 或 git revert + push | < 3min |
| Modal函数 | `modal deploy` 上一版本代码 | < 5min |
| 数据库迁移 | 执行 down.sql 回滚脚本 | < 10min |
| Chroma索引 | 切换到旧索引目录(保留24h) | < 1min |

## 6. 备份策略

| 数据 | 方式 | 频率 | 保留 | 存储 |
|------|------|------|------|------|
| PostgreSQL | Supabase自动备份 | 每日 | 7天 | Supabase内置 |
| PostgreSQL | pg_dump手动 | 每周 | 30天 | S3 |
| Chroma向量库 | 目录快照 | 每周 | 4周 | S3 |
| 用户代码 | PostgreSQL中已含 | 随DB备份 | 同上 | - |
| Redis | 不持久化(可重建) | - | - | - |
| 环境变量 | 1Password团队保管库 | 变更时 | 永久 | 1Password |
