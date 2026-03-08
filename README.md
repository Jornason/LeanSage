# LeanSage — AI-Powered Lean 4 Proof Assistant

> AI assistant that searches 200K+ Mathlib theorems, generates proof drafts from natural language, and diagnoses tactic errors in Lean 4.

## Project Overview

LeanSage is an AI-powered SaaS tool that flattens the steep learning curve of formal proof in Lean 4. It indexes 200,000+ Mathlib theorems into a vector database for semantic search, generates compilable proof drafts from natural language descriptions, and provides real-time error diagnosis with fix suggestions — all through a web-based CodeMirror editor with Lean 4 syntax highlighting and KaTeX formula rendering.

## Core Features (P0)

| Feature | Description |
|---------|-------------|
| Mathlib Semantic Search | Natural language → top-K relevant theorems (80% recall target) |
| Proof Draft Generation | Natural language description → Lean 4 code (40%+ compile rate) |
| Error Diagnosis | Analyze tactic errors with fix suggestions (<5s, ≥70% accuracy) |
| Code Editor | CodeMirror with Lean 4 syntax highlighting + KaTeX rendering |
| Auth & Billing | GitHub OAuth + Stripe subscriptions (Free/Researcher/Lab) |
| Lean 4 Compilation | Server-side Lean 4 LSP via Modal.com GPU instances |

## Tech Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 14 + CodeMirror + KaTeX | Web app, code editing, formula rendering |
| Backend | Python FastAPI | API service |
| AI Engine | Claude API (claude-3-5-sonnet) | Proof generation, error diagnosis |
| Proof Engine | Lean 4 LSP + mathlib4 | Real-time compilation checking |
| Vector DB | Chroma | ~200K Mathlib theorem semantic search |
| Embeddings | OpenAI text-embedding-3-small | Vectorization |
| Database | Supabase (PostgreSQL + Auth) | User data, session management |
| Compute | Modal.com | On-demand GPU for Lean checking |
| Deployment | Vercel + Modal.com | Frontend hosting + backend compute |

## Quick Start

### 1. Python Environment (conda)

```bash
# Create and activate the conda environment
conda create -n leansage python=3.11 -y
conda activate leansage
```

### 2. Backend (FastAPI · port 8005)

```bash
cd dev/backend

# Install dependencies
pip install -r requirements.txt

# Copy env template and fill in your API keys
cp .env.example .env   # or edit .env directly

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

API docs available at: http://localhost:8005/docs

### 3. Frontend (Next.js · port 3005)

```bash
cd dev/frontend

# Install dependencies (requires pnpm)
pnpm install

# Start the dev server on port 3005
pnpm dev -- --port 3005
```

App available at: http://localhost:3005

### 4. Demo Mode (no login required)

Visit **http://localhost:3005/demo** — the page auto-logs in as the built-in demo
account (`demo@leanprove.ai`) and redirects to the Search page. No registration needed.

> **Demo credentials** (also works on the login page):
> - Email: `demo@leanprove.ai`
> - Password: `demo12345`

### 5. Lean toolchain (optional)

```bash
# Requires elan pre-installed
elan install leanprover/lean4:v4.8.0
lake build
```

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| Free | $0/mo | 10 queries |
| Researcher | $19/mo | Unlimited queries + proof generation |
| Lab | $49/mo | Team collaboration + priority compilation |
| Institution | $2,000–$50,000/yr | University/enterprise bulk license |

## Key Metrics

- Target: 5,000 users in 6 months, 500 paid
- 80% Top-5 recall for Mathlib search
- 45% compile rate for generated proofs
- $15k MRR target

## Docs

| File | Purpose |
|------|---------|
| `01-PRD.md` | Product requirements & acceptance criteria |
| `02-ARCHITECTURE.md` | System architecture & Lean 4 integration |
| `03-API-SPEC.md` | REST API specifications |
| `04-DATA-MODEL.md` | Database schema & vector store design |
| `05-UI-DESIGN.md` | UI/UX design system & editor layout |
| `06-IMPLEMENTATION.md` | Milestones & task breakdown |
| `07-TESTING.md` | Test plan & accuracy benchmarks |
| `08-DEPLOYMENT.md` | Deployment & GPU provisioning |
| `09-CHANGELOG.md` | Change log |
| `CLAUDE.md` | Claude Code project context |
