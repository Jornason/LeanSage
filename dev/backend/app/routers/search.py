"""
Mathlib Semantic Search Router
POST /v1/search/mathlib
"""

import time
import random
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.api import SearchRequest, SearchResponse, TheoremResult
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota,
)

router = APIRouter()

# Mock Mathlib theorem database for development
# In production, this would query Chroma vector DB
MOCK_THEOREMS = [
    {
        "theorem_name": "Continuous.add",
        "full_name": "Mathlib.Topology.ContinuousOn.add",
        "type_signature": "theorem Continuous.add {f g : α → β} [TopologicalSpace α] [TopologicalSpace β] [Add β] [ContinuousAdd β] (hf : Continuous f) (hg : Continuous g) : Continuous (fun x => f x + g x)",
        "module": "Mathlib.Topology.Algebra.Group.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/Group/Basic.html",
        "keywords": ["continuous", "add", "sum", "topology"],
    },
    {
        "theorem_name": "ContinuousOn.add",
        "full_name": "Mathlib.Topology.ContinuousOn.add",
        "type_signature": "theorem ContinuousOn.add {f g : α → β} {s : Set α} (hf : ContinuousOn f s) (hg : ContinuousOn g s) : ContinuousOn (fun x => f x + g x) s",
        "module": "Mathlib.Topology.Algebra.Group.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Algebra/Group/Basic.html",
        "keywords": ["continuousOn", "add", "set", "topology"],
    },
    {
        "theorem_name": "tendsto_nhds_unique",
        "full_name": "Mathlib.Topology.Basic.tendsto_nhds_unique",
        "type_signature": "theorem tendsto_nhds_unique {f : β → α} {l : Filter β} {a b : α} [T2Space α] (hl : NeBot l) (ha : Tendsto f l (nhds a)) (hb : Tendsto f l (nhds b)) : a = b",
        "module": "Mathlib.Topology.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Basic.html",
        "keywords": ["limit", "unique", "tendsto", "nhds"],
    },
    {
        "theorem_name": "Continuous.comp",
        "full_name": "Mathlib.Topology.Basic.Continuous.comp",
        "type_signature": "theorem Continuous.comp {f : β → γ} {g : α → β} (hf : Continuous f) (hg : Continuous g) : Continuous (f ∘ g)",
        "module": "Mathlib.Topology.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Basic.html",
        "keywords": ["continuous", "composition", "compose"],
    },
    {
        "theorem_name": "IsCompact.isClosed",
        "full_name": "Mathlib.Topology.Compactness.IsCompact.isClosed",
        "type_signature": "theorem IsCompact.isClosed [T2Space α] {s : Set α} (hs : IsCompact s) : IsClosed s",
        "module": "Mathlib.Topology.Compactness.Compact",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Topology/Compactness/Compact.html",
        "keywords": ["compact", "closed", "T2", "Hausdorff"],
    },
    {
        "theorem_name": "Nat.add_zero",
        "full_name": "Mathlib.Init.Data.Nat.Basic.Nat.add_zero",
        "type_signature": "theorem Nat.add_zero (n : ℕ) : n + 0 = n",
        "module": "Mathlib.Init.Data.Nat.Basic",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Init/Data/Nat/Basic.html",
        "keywords": ["natural", "addition", "zero", "identity"],
    },
    {
        "theorem_name": "Real.sqrt_sq",
        "full_name": "Mathlib.Analysis.SpecialFunctions.Pow.Real.Real.sqrt_sq",
        "type_signature": "theorem Real.sqrt_sq {x : ℝ} (h : 0 ≤ x) : √(x ^ 2) = x",
        "module": "Mathlib.Analysis.SpecialFunctions.Pow.Real",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/SpecialFunctions/Pow/Real.html",
        "keywords": ["sqrt", "square root", "power", "real"],
    },
    {
        "theorem_name": "Int.ModEq",
        "full_name": "Mathlib.Data.Int.ModCast.Int.ModEq",
        "type_signature": "def Int.ModEq (n a b : ℤ) : Prop := a % n = b % n",
        "module": "Mathlib.Data.Int.ModCast",
        "doc_url": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Data/Int/ModCast.html",
        "keywords": ["modular", "congruence", "integer"],
    },
]


def mock_search(query: str, top_k: int, filter_module: Optional[str]) -> list:
    """
    Mock semantic search -- in production uses Chroma vector similarity.
    Simulates relevance scoring with keyword matching + random noise.
    """
    query_lower = query.lower()
    scored = []
    for theorem in MOCK_THEOREMS:
        # Simple keyword matching for mock
        score = 0.5  # base
        for kw in theorem["keywords"]:
            if kw in query_lower:
                score += 0.15
        # Add some noise
        score += random.uniform(-0.05, 0.05)
        score = max(0.3, min(0.99, score))

        if filter_module and filter_module.lower() not in theorem["module"].lower():
            continue

        scored.append((score, theorem))

    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


@router.post("/search/mathlib")
async def search_mathlib(
    request: SearchRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Semantic search over Mathlib theorems using natural language query.
    Returns Top-K results ranked by semantic similarity.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    start = time.time()
    embedding_time = 120  # mock embedding time

    results_raw = mock_search(request.query, request.top_k, request.filter_module)

    search_time = int((time.time() - start) * 1000)

    results = [
        TheoremResult(
            rank=i + 1,
            theorem_name=t["theorem_name"],
            full_name=t["full_name"],
            type_signature=t["type_signature"],
            module=t["module"],
            doc_url=t["doc_url"],
            similarity=round(score, 3),
        )
        for i, (score, t) in enumerate(results_raw)
    ]

    return ok(
        SearchResponse(
            results=results,
            total_results=len(results),
            query_embedding_time_ms=embedding_time,
            search_time_ms=search_time,
        ).model_dump()
    )
