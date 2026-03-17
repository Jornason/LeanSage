# 部署文档 - LeanProve AI

## 目录

1. [部署架构概览](#1-部署架构概览)
2. [服务器要求](#2-服务器要求)
3. [首次部署（完整流程）](#3-首次部署完整流程)
4. [目录结构说明](#4-目录结构说明)
5. [Docker 配置详解](#5-docker-配置详解)
6. [环境变量说明](#6-环境变量说明)
7. [日常更新部署](#7-日常更新部署)
8. [验证与自测](#8-验证与自测)
9. [常见问题排查](#9-常见问题排查)
10. [回滚方案](#10-回滚方案)
11. [监控与运维](#11-监控与运维)
12. [备份策略](#12-备份策略)

---

## 1. 部署架构概览

```
本地开发机
    │
    │  rsync（同步代码）
    ▼
服务器 47.242.43.35 (Ubuntu 22.04, Docker 24.0)
    │
    ├── leansage-frontend  (Next.js, 3029:3000, production)
    ├── leansage-backend   (FastAPI, 9019:8000, production)
    └── leansage-redis     (Redis 7, 内部 6379, 不对外暴露)
            │
            │  HTTP (OpenAI-compatible streaming)
            ▼
    aws-gpt-5.4  http://3.27.111.18:8080/api/v1
```

**端口分配**

| 服务 | 容器内端口 | 宿主机端口 | 对外访问 URL |
|------|-----------|-----------|-------------|
| Frontend (Next.js) | 3000 | **3029** | http://47.242.43.35:3029 |
| Backend (FastAPI) | 8000 | **9019** | http://47.242.43.35:9019 |
| API 文档 (Swagger) | 8000 | 9019 | http://47.242.43.35:9019/docs |
| Redis | 6379 | 不暴露 | leansage-net 内部 |

> 端口选用 9xxx 段，避开服务器已占用的 9010（agentcareer）、9001（agwallet）等端口。

---

## 2. 服务器要求

| 项目 | 要求 | 说明 |
|------|------|------|
| OS | Ubuntu 20.04+ / Debian 11+ | 测试环境：Ubuntu 22.04 |
| CPU | 2核+ | 构建 Next.js 需要 ≥ 1.5GB 内存 |
| 内存 | 4GB+ | 前端 standalone 构建峰值约 1.2GB |
| 磁盘 | 20GB+ | 镜像：backend≈505MB，frontend≈169MB |
| Docker | 20.10+ | 测试版本：24.0.7 |
| Docker Compose | v2.x | 测试版本：v2.21.0 |
| 网络 | 80/443/3029/9019 入站开放 | 或按需配置 |

**安装 Docker（如未安装）**

```bash
# Ubuntu/Debian 一键安装
curl -fsSL https://get.docker.com | sh

# 验证
docker --version        # Docker version 24.x.x
docker compose version  # Docker Compose version v2.x.x
```

---

## 3. 首次部署（完整流程）

### 步骤 1：在本地克隆仓库并确认文件完整

```bash
git clone git@github.com:Jornason/LeanSage.git
cd LeanSage

# 确认以下关键文件存在
ls dev/docker-compose.yml
ls dev/backend/Dockerfile
ls dev/frontend/Dockerfile
ls dev/backend/app/core/ai_client.py
```

### 步骤 2：SSH 登录服务器，创建部署目录

```bash
ssh root@47.242.43.35

# 创建部署根目录
mkdir -p ~/leansage
exit
```

### 步骤 3：从本地同步代码到服务器

在**本地**仓库根目录执行：

```bash
rsync -avz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='.env.local' \
  --exclude='venv' \
  --exclude='.git' \
  dev/ root@47.242.43.35:~/leansage/
```

> **说明**：只同步 `dev/` 目录内容到服务器 `~/leansage/`。
> `node_modules`、`.next`、`__pycache__` 等构建产物不需要传输，在服务器上由 Docker 构建生成。

同步完成后，服务器目录结构应如下：

```
~/leansage/
├── docker-compose.yml       # 主编排文件
├── .env.example             # 环境变量模板
├── admin-credentials.json   # 管理员账号（本地记录）
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── core/
│       │   ├── config.py
│       │   ├── auth.py
│       │   └── ai_client.py   # aws-gpt-5.4 客户端
│       ├── routers/
│       └── schemas/
└── frontend/
    ├── Dockerfile
    ├── .dockerignore
    ├── package.json
    ├── pnpm-lock.yaml
    ├── next.config.js
    └── app/
```

### 步骤 4：（可选）创建 .env 覆盖默认配置

```bash
ssh root@47.242.43.35
cd ~/leansage

# docker-compose.yml 已内置所有默认值，如需覆盖则创建 .env
cat > .env << 'EOF'
# 覆盖 JWT 密钥（强烈建议在生产环境中替换）
JWT_SECRET_KEY=your-very-secret-production-key-change-this

# 可选：接入真实数据库
DATABASE_URL=postgresql://user:pass@host:5432/leansage

# 可选：其他 AI 备用 key
ANTHROPIC_API_KEY=sk-ant-xxxxx
OPENAI_API_KEY=sk-xxxxx

# 可选：Stripe 支付
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
EOF
```

> **注意**：`AWS_GPT_BASE_URL`、`AWS_GPT_API_KEY`、`AWS_GPT_MODEL` 已直接写入 `docker-compose.yml`，无需在 `.env` 中重复声明。

### 步骤 5：构建并启动所有容器

```bash
cd ~/leansage

# 首次部署：构建镜像并启动（--build 强制重新构建）
docker compose up -d --build
```

构建过程预计耗时：

| 阶段 | 耗时（首次） | 说明 |
|------|------------|------|
| backend pip install | ~60s | 安装约 40 个 Python 包 |
| frontend pnpm install | ~90s | 安装 node_modules |
| frontend next build | ~120s | 编译 TypeScript + 生成 standalone |
| 镜像导出 | ~10s | |

### 步骤 6：确认容器运行状态

```bash
docker compose ps
```

预期输出：

```
NAME                IMAGE               COMMAND                                             SERVICE    STATUS
leansage-backend    leansage-backend    "uvicorn app.main:app --host 0.0.0.0 --port 8000"   backend    Up X minutes
leansage-frontend   leansage-frontend   "node server.js"                                    frontend   Up X minutes
leansage-redis      redis:7-alpine      "docker-entrypoint.sh redis-server"                 redis      Up X minutes
```

所有容器 STATUS 列均显示 `Up` 即为成功。

---

## 4. 目录结构说明

### 后端 Dockerfile 解析

```dockerfile
FROM python:3.11-slim              # 精简镜像，减小体积

RUN apt-get install -y gcc libpq-dev  # psycopg2 编译依赖

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .                           # .dockerignore 排除了 venv/__pycache__/.env/tests/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**后端 .dockerignore**（排除内容）：
```
venv/          # 本地 conda/venv 环境
__pycache__/   # Python 字节码
*.pyc
.env           # 不把密钥打进镜像
tests/         # 测试文件不需要在生产中
.pytest_cache/
.git/
```

### 前端 Dockerfile 解析（多阶段构建）

```dockerfile
# 阶段1: deps — 只安装依赖
FROM node:18-alpine AS deps
RUN corepack enable && corepack prepare pnpm@latest --activate
COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

# 阶段2: builder — 编译
FROM base AS builder
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ARG NEXT_PUBLIC_API_URL           # 构建时注入后端地址
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
RUN pnpm build                    # 生成 .next/standalone

# 阶段3: runner — 最小生产镜像（只含 standalone 产物）
FROM node:18-alpine AS runner
ENV NODE_ENV=production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
CMD ["node", "server.js"]         # 不使用 next start，直接跑 Node.js
```

> **关键**：`next.config.js` 中必须有 `output: "standalone"` 才能生成 `server.js`。

**前端 .dockerignore**（排除内容）：
```
node_modules/  # 由 Docker 内部安装
.next/         # 由 Docker 内部构建
.env.local
.env
.git/
*.md
```

---

## 5. Docker 配置详解

### docker-compose.yml 关键配置

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: leansage-backend
    ports:
      - "9019:8000"          # 宿主机:容器
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
      - JWT_SECRET_KEY=${JWT_SECRET_KEY:-leansage-production-jwt-secret-key-2026}
      - REDIS_URL=redis://redis:6379           # 容器内网络通信，用服务名
      - FRONTEND_URL=http://47.242.43.35:3029
      - CORS_ORIGINS=http://47.242.43.35:3029,http://localhost:3029
      # aws-gpt-5.4 主 AI 模型（已内置，无需 .env）
      - AWS_GPT_BASE_URL=http://3.27.111.18:8080/api
      - AWS_GPT_API_KEY=cr_232256050a613cfe0e6e87581ee12316472561743170a9daf9ce9ddf3d8262d8
      - AWS_GPT_MODEL=gpt-5.4
    depends_on:
      - redis
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - NEXT_PUBLIC_API_URL=http://47.242.43.35:9019/v1   # 构建时烘焙进去
    container_name: leansage-frontend
    ports:
      - "3029:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: leansage-redis
    volumes:
      - redis-data:/data      # 数据持久化
    restart: unless-stopped
    # 无 ports 暴露 — 仅限内部网络访问

networks:
  leansage-net:
    driver: bridge            # 三个容器在同一内部网络
```

> **`NEXT_PUBLIC_API_URL` 的特殊性**：Next.js 的 `NEXT_PUBLIC_` 前缀变量在**构建时**被静态内联到 JS bundle，运行时修改环境变量无效。因此必须在 `docker-compose.yml` 的 `build.args` 中传入，而不是 `environment`。

---

## 6. 环境变量说明

### 已内置（docker-compose.yml 中有默认值，无需手动配置）

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `AWS_GPT_BASE_URL` | `http://3.27.111.18:8080/api` | 主 AI 服务地址 |
| `AWS_GPT_API_KEY` | `cr_232...` | aws-gpt-5.4 API Key |
| `AWS_GPT_MODEL` | `gpt-5.4` | 模型名称 |
| `JWT_SECRET_KEY` | `leansage-production-jwt-secret-key-2026` | **建议生产环境替换** |
| `JWT_EXPIRE_MINUTES` | `10080` | Token 有效期 7 天 |
| `REDIS_URL` | `redis://redis:6379` | 容器内 Redis 地址 |
| `FRONTEND_URL` | `http://47.242.43.35:3029` | CORS 允许来源 |
| `NEXT_PUBLIC_API_URL` | `http://47.242.43.35:9019/v1` | 前端调用后端地址（构建时注入） |

### 可选覆盖（通过 .env 文件）

| 变量 | 说明 |
|------|------|
| `JWT_SECRET_KEY` | 生产环境务必替换为随机强密钥 |
| `DATABASE_URL` | PostgreSQL 连接串（当前用内存存储，可选） |
| `ANTHROPIC_API_KEY` | Claude API Key（备用 AI） |
| `OPENAI_API_KEY` | OpenAI Key（备用 AI / Embedding） |
| `STRIPE_SECRET_KEY` | Stripe 支付密钥 |
| `STRIPE_WEBHOOK_SECRET` | Stripe Webhook 签名验证 |

### 生成强 JWT 密钥

```bash
# 本地生成随机 32 字节密钥
python3 -c "import secrets; print(secrets.token_hex(32))"
# 或
openssl rand -hex 32
```

---

## 7. 日常更新部署

### 场景一：代码有变更，需要重新部署

```bash
# 1. 本地提交代码
git add .
git commit -m "feat: xxx"
git push

# 2. 同步到服务器（从本地仓库根目录执行）
rsync -avz \
  --exclude='node_modules' \
  --exclude='.next' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  --exclude='.env.local' \
  --exclude='venv' \
  --exclude='.git' \
  dev/ root@47.242.43.35:~/leansage/

# 3. 登录服务器重建对应服务
ssh root@47.242.43.35
cd ~/leansage

# 只重建后端（后端代码有变更时）
docker compose build --no-cache backend
docker compose up -d backend

# 只重建前端（前端代码有变更时）
docker compose build --no-cache frontend
docker compose up -d frontend

# 前后端都有变更时，全部重建
docker compose build --no-cache
docker compose up -d
```

### 场景二：只修改了后端（Python）代码

```bash
# 同步后端文件
rsync -avz \
  --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
  dev/backend/ root@47.242.43.35:~/leansage/backend/

# 重建后端
ssh root@47.242.43.35 "cd ~/leansage && \
  docker compose build --no-cache backend && \
  docker compose up -d backend"
```

### 场景三：修改了环境变量

```bash
ssh root@47.242.43.35
cd ~/leansage

# 编辑 .env 文件
nano .env

# 重启对应服务（不需要重新构建）
docker compose up -d backend   # 环境变量变更只需重启，不需 rebuild
```

> **例外**：修改 `NEXT_PUBLIC_API_URL` 必须重新 build 前端（该变量在构建时内联）。

---

## 8. 验证与自测

### 基础健康检查

```bash
# 后端健康
curl http://47.242.43.35:9019/health
# 期望: {"status":"healthy","version":"0.1.0","environment":"production"}

# 前端可访问
curl -I http://47.242.43.35:3029
# 期望: HTTP/1.1 200 OK
```

### 完整 API 自测脚本

```bash
#!/bin/bash
set -e

BASE="http://47.242.43.35:9019"
echo "=== LeanSage 生产环境自测 ==="

# 1. 健康检查
echo -n "1. 健康检查... "
curl -sf $BASE/health | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['status']=='healthy'"
echo "✓"

# 2. Admin 登录
echo -n "2. Admin 登录... "
TOKEN=$(curl -sf -X POST $BASE/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@leanprove.ai","password":"admin12345"}' \
  | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['access_token'])")
echo "✓ Token: ${TOKEN:0:20}..."

AUTH="-H \"Authorization: Bearer $TOKEN\""

# 3. 证明生成（测试 aws-gpt-5.4）
echo -n "3. 证明生成 (aws-gpt-5.4)... "
RESULT=$(curl -sf -X POST $BASE/v1/generate/proof \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"description":"Prove that n + 0 = n for natural numbers"}')
CONF=$(echo $RESULT | python3 -c "import json,sys; print(json.load(sys.stdin)['data']['confidence'])")
echo "✓ confidence=$CONF"

# 4. 错误诊断
echo -n "4. 错误诊断... "
curl -sf -X POST $BASE/v1/diagnose/error \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"code":"theorem foo : 1+1=3 := by ring","error_message":"type mismatch"}' > /dev/null
echo "✓"

# 5. Mathlib 搜索
echo -n "5. Mathlib 搜索... "
curl -sf -X POST $BASE/v1/search/mathlib \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query":"commutativity of addition","limit":3}' > /dev/null
echo "✓"

echo ""
echo "=== 全部测试通过 ✓ ==="
echo "Frontend: http://47.242.43.35:3029"
echo "Backend:  http://47.242.43.35:9019"
echo "API Docs: http://47.242.43.35:9019/docs"
```

将以上脚本保存为 `scripts/selftest.sh`，运行：

```bash
bash scripts/selftest.sh
```

### 查看容器日志

```bash
# 实时日志
docker compose -f ~/leansage/docker-compose.yml logs -f backend
docker compose -f ~/leansage/docker-compose.yml logs -f frontend

# 最近 100 行
docker logs leansage-backend --tail 100
docker logs leansage-frontend --tail 100

# 过滤错误
docker logs leansage-backend 2>&1 | grep -i error
```

---

## 9. 常见问题排查

### 问题 1：容器名冲突

**现象**：`docker compose up` 报错 `container name "/leansage-xxx" already in use`

**原因**：上次容器未正常停止，残留了同名容器。

**解决**：
```bash
docker rm -f leansage-backend leansage-frontend leansage-redis
docker compose up -d --build
```

### 问题 2：端口被占用

**现象**：`bind: address already in use` 或容器启动后立即退出。

**排查**：
```bash
# 查看端口占用
ss -tlnp | grep -E '9019|3029'
# 或
lsof -i :9019

# 查看所有 docker 占用端口（排查与其他项目冲突）
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -v "^NAME"
```

**解决**：修改 `docker-compose.yml` 中的宿主机端口映射（左侧端口），换一个未被占用的 9xxx 端口。

### 问题 3：前端调用后端失败（CORS / API 地址错误）

**现象**：浏览器 Network 面板显示 CORS 错误，或请求打到了错误地址。

**根本原因**：`NEXT_PUBLIC_API_URL` 在构建时被内联，修改环境变量后需要**重新 build 前端**。

**排查**：
```bash
# 进入前端容器，查看实际内联的 API 地址
docker exec leansage-frontend sh -c "grep -r 'NEXT_PUBLIC_API_URL\|9019\|9010' /app/.next/server/ 2>/dev/null | head -5"
```

**解决**：
```bash
# 修改 docker-compose.yml 中 frontend.build.args 的 NEXT_PUBLIC_API_URL
# 然后重新构建前端
docker compose build --no-cache frontend
docker compose up -d frontend
```

### 问题 4：AI 接口返回降级数据（confidence: 0.4）

**现象**：`/v1/generate/proof` 返回的 `confidence` 为 `0.4`（降级），而非 `0.85`（AI 真实响应）。

**原因**：aws-gpt-5.4 服务不可达，`ai_client.py` 的 `chat()` 返回了 `None`，路由使用了 fallback 逻辑。

**排查**：
```bash
# 在服务器上直接测试 AI 服务连通性
curl -s -X POST http://3.27.111.18:8080/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer cr_232256050a613cfe0e6e87581ee12316472561743170a9daf9ce9ddf3d8262d8" \
  -d '{"model":"gpt-5.4","messages":[{"role":"user","content":"hi"}],"stream":true}' \
  --max-time 10

# 查看后端日志中的异常
docker logs leansage-backend --tail 50 | grep -i "exception\|error\|traceback"
```

### 问题 5：构建时 Next.js 内存不足

**现象**：`docker compose build frontend` 时容器被 OOM Kill，或报 `JavaScript heap out of memory`。

**解决**：
```bash
# 增大 Node.js 堆内存限制（在 Dockerfile builder 阶段添加）
ENV NODE_OPTIONS="--max-old-space-size=2048"
RUN pnpm build
```

### 问题 6：bcrypt 相关报错

**现象**：`AttributeError: module 'bcrypt' has no attribute '__about__'`

**原因**：`passlib` 与新版 `bcrypt>=4.1` 不兼容。

**解决**：确认 `requirements.txt` 中使用 `bcrypt>=4.0.0`，**不使用** `passlib`。`auth.py` 应直接调用 `bcrypt.hashpw` / `bcrypt.checkpw`。

---

## 10. 回滚方案

### 快速回滚（重启上一个镜像）

Docker Compose 不自动保留旧镜像，但可以通过 git 回退代码再重建：

```bash
# 1. 本地 git 回退
git revert HEAD          # 创建回退 commit
git push

# 2. 同步到服务器
rsync -avz --exclude='node_modules' --exclude='.next' \
  --exclude='__pycache__' --exclude='.env' \
  dev/ root@47.242.43.35:~/leansage/

# 3. 重建并重启
ssh root@47.242.43.35 "cd ~/leansage && \
  docker compose build --no-cache && \
  docker compose up -d"
```

### 保留旧镜像（推荐生产环境）

部署新版前先为旧镜像打 tag：

```bash
ssh root@47.242.43.35

# 部署前打 tag 备份
docker tag leansage-backend leansage-backend:backup-$(date +%Y%m%d)
docker tag leansage-frontend leansage-frontend:backup-$(date +%Y%m%d)

# 构建新版
cd ~/leansage
docker compose build --no-cache
docker compose up -d

# 回滚时（恢复旧镜像）
docker stop leansage-backend
docker rm leansage-backend
docker run -d \
  --name leansage-backend \
  --network leansage_leansage-net \
  -p 9019:8000 \
  --env-file .env \
  leansage-backend:backup-20260317
```

---

## 11. 监控与运维

### 查看资源占用

```bash
# 所有容器实时资源
docker stats leansage-backend leansage-frontend leansage-redis

# 磁盘占用
docker system df
```

### 清理磁盘空间

```bash
# 清理未使用的镜像、容器、网络（不清 volume）
docker system prune -f

# 清理所有未使用 volume（谨慎：会删 Redis 数据）
docker volume prune -f
```

### 定期检查服务状态

```bash
# 查看容器运行时长和重启次数
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.RunningFor}}"

# 检查 Redis 连接
docker exec leansage-redis redis-cli ping
# 期望: PONG
```

---

## 12. 备份策略

| 数据 | 当前方案 | 说明 |
|------|---------|------|
| Redis | Docker Volume `redis-data` 持久化 | 服务器重启不丢失；容器删除前执行 `docker run --rm -v redis-data:/data -v $(pwd):/backup alpine tar czf /backup/redis-backup.tar.gz /data` |
| 用户数据 | 内存存储（MOCK_USERS）| 容器重启后重置；接入 PostgreSQL 后由数据库持久化 |
| 代码 | GitHub 仓库 | 所有变更均通过 git 管理 |
| 环境变量 | 服务器 `~/leansage/.env` | 建议额外备份到安全位置（1Password 等） |
| admin 账号 | `dev/admin-credentials.json`（本地）| 不提交到 git，本地妥善保管 |

### Redis 数据备份

```bash
ssh root@47.242.43.35

# 备份
docker run --rm \
  -v leansage_redis-data:/data \
  -v ~/backups:/backup \
  alpine tar czf /backup/redis-$(date +%Y%m%d).tar.gz /data

# 恢复
docker run --rm \
  -v leansage_redis-data:/data \
  -v ~/backups:/backup \
  alpine tar xzf /backup/redis-20260317.tar.gz -C /
```

---

## 账号信息

### 管理员账号（最高权限）

```
Email:    admin@leanprove.ai
Password: admin12345
Role:     admin
权限:     无限配额，120 次/分钟速率限制，所有功能全部开放
```

### Demo 账号（Researcher 权限）

```
Email:    demo@leanprove.ai
Password: demo12345
Role:     researcher
```

也可访问 `/demo` 路由自动免密登录 demo 账号。

---

## 快速参考

```bash
# 启动所有服务
cd ~/leansage && docker compose up -d

# 停止所有服务
cd ~/leansage && docker compose down

# 重建并重启（代码更新后）
cd ~/leansage && docker compose build --no-cache && docker compose up -d

# 查看日志
docker compose -f ~/leansage/docker-compose.yml logs -f

# 健康检查
curl http://47.242.43.35:9019/health

# 服务访问地址
# 前端:     http://47.242.43.35:3029
# 后端 API: http://47.242.43.35:9019
# API 文档: http://47.242.43.35:9019/docs
```
