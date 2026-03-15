# LeanProve AI - Development README

## Quick Start

### Prerequisites
- Node.js 18+ and pnpm
- Python 3.11+ (via Conda)
- (Optional) PostgreSQL for production data

### Backend (Python + Conda)

```bash
# 1. Create conda environment
conda create -n leansage python=3.11 -y

# 2. Activate environment
conda activate leansage

# 3. Install dependencies
cd dev/backend
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env   # Edit with your API keys

# 5. Start development server
uvicorn app.main:app --reload --port 8005
# API docs at http://localhost:8005/docs
```

### Frontend (Next.js)

```bash
cd dev/frontend
pnpm install
pnpm dev -- --port 3005
# Opens at http://localhost:3005
```

### Running Tests

```bash
# Backend API tests (37 test cases)
cd dev/backend
conda activate leansage
pytest tests/test_api.py -v
```

```bash
# Frontend type check + build
cd dev/frontend
pnpm build
```

---

## Project Structure

```
dev/
├── frontend/               # Next.js 14 App Router
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   ├── globals.css          # Global styles (dark theme)
│   │   ├── demo/                # Demo auto-login
│   │   ├── (auth)/login/        # Auth pages
│   │   └── (app)/               # Authenticated app
│   │       ├── layout.tsx       # App shell with nav
│   │       ├── search/          # Mathlib semantic search
│   │       ├── workspace/       # Lean 4 IDE
│   │       ├── diagnose/        # Error diagnosis
│   │       ├── convert/         # LaTeX↔Lean converter
│   │       ├── dashboard/       # User dashboard
│   │       ├── pricing/         # Subscription plans
│   │       └── settings/        # User settings
│   ├── components/
│   │   ├── editor/LeanEditor.tsx    # CodeMirror 6 editor
│   │   └── math/MathFormula.tsx     # KaTeX rendering
│   └── lib/api.ts               # API client
│
└── backend/                # FastAPI Python backend
    ├── app/
    │   ├── main.py              # App entry point
    │   ├── core/
    │   │   ├── config.py        # Settings (Pydantic)
    │   │   └── auth.py          # JWT + RBAC + quota
    │   ├── schemas/
    │   │   ├── api.py           # Request/response schemas
    │   │   └── common.py        # Shared response format
    │   ├── models/
    │   │   └── database.py      # SQLAlchemy ORM models
    │   └── routers/
    │       ├── search.py        # POST /v1/search/mathlib
    │       ├── generate.py      # POST /v1/generate/proof
    │       ├── diagnose.py      # POST /v1/diagnose/error
    │       ├── convert.py       # POST /v1/convert/*
    │       ├── compile.py       # POST /v1/compile/check
    │       ├── explain.py       # POST /v1/explain/tactics
    │       ├── auth.py          # POST /v1/auth/*
    │       ├── user.py          # GET  /v1/user/*
    │       ├── proof.py         # CRUD /v1/proof/sessions
    │       └── billing.py       # Subscription & billing
    └── tests/
        └── test_api.py          # 37 API test cases
```

---

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Landing | `/` | Hero, features, pricing |
| Login | `/login` | Email + GitHub OAuth |
| Demo | `/demo` | Auto-login as demo user |
| Search | `/search` | Mathlib semantic search |
| Workspace | `/workspace` | 3-pane Lean 4 IDE |
| Diagnose | `/diagnose` | Error analysis + fixes |
| Convert | `/convert` | LaTeX↔Lean converter |
| Dashboard | `/dashboard` | Stats + session history |
| Pricing | `/pricing` | Subscription plans |
| Settings | `/settings` | User preferences |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/auth/login` | Email/password login |
| POST | `/v1/auth/register` | User registration |
| POST | `/v1/auth/demo` | Demo access (no registration) |
| GET | `/v1/auth/github` | GitHub OAuth start |
| GET | `/v1/auth/github/callback` | GitHub OAuth callback |
| POST | `/v1/search/mathlib` | Semantic theorem search |
| POST | `/v1/generate/proof` | AI proof generation |
| POST | `/v1/diagnose/error` | Error diagnosis |
| POST | `/v1/convert/latex-to-lean` | LaTeX→Lean conversion |
| POST | `/v1/convert/lean-to-latex` | Lean→LaTeX conversion |
| POST | `/v1/compile/check` | Lean 4 compilation check |
| POST | `/v1/explain/tactics` | Tactic explanation |
| GET | `/v1/user/usage` | Usage statistics |
| GET | `/v1/user/profile` | User profile |
| GET | `/v1/proof/sessions` | List proof sessions |
| POST | `/v1/proof/sessions` | Create session |
| GET | `/v1/proof/sessions/{id}` | Get session |
| PATCH | `/v1/proof/sessions/{id}` | Update session |
| DELETE | `/v1/proof/sessions/{id}` | Delete session |
| GET | `/v1/billing/subscription` | Get subscription |
| POST | `/v1/billing/create-checkout` | Create Stripe checkout |
| POST | `/v1/billing/cancel` | Cancel subscription |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 14, TypeScript, Tailwind CSS |
| Code Editor | CodeMirror 6 |
| Math Rendering | KaTeX |
| Charts | Recharts |
| Backend | FastAPI, Python 3.11 (Conda) |
| ORM | SQLAlchemy 2 |
| Auth | JWT (python-jose) + bcrypt |
| Database | PostgreSQL (Supabase) |
| AI | Claude API (Anthropic) |
| Search | Chroma Vector DB |
| Lean Compiler | Modal.com |
| Payments | Stripe |

---

## Environment Variables

Copy `.env.example` to `.env` in the backend directory and fill in the values:

| Variable | Description |
|----------|-------------|
| `JWT_SECRET_KEY` | Secret for JWT signing |
| `ANTHROPIC_API_KEY` | Claude API key |
| `OPENAI_API_KEY` | OpenAI API key (embeddings) |
| `GITHUB_CLIENT_ID/SECRET` | GitHub OAuth app |
| `STRIPE_SECRET_KEY` | Stripe payments |
| `DATABASE_URL` | PostgreSQL connection |
| `REDIS_URL` | Redis cache |

---

## Demo Credentials

```
Email: demo@leanprove.ai
Password: demo12345
```

Or visit `/demo` for instant auto-login.
