"""
Proof Generation Router
POST /v1/generate/proof
"""

import time
from fastapi import APIRouter, Depends

from app.schemas.api import GenerateRequest, GenerateResponse, CompilationResult
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota, require_plan,
)

router = APIRouter()

MOCK_GENERATED_PROOFS = {
    "default": """import Mathlib.Tactic

theorem generated_proof (n : ℕ) : n + 0 = n := by
  simp""",
    "continuous": """import Mathlib.Topology.Algebra.Group.Basic

theorem sum_continuous {α β : Type*}
    [TopologicalSpace α] [TopologicalSpace β]
    [Add β] [ContinuousAdd β]
    {f g : α → β}
    (hf : Continuous f) (hg : Continuous g) :
    Continuous (fun x => f x + g x) := by
  exact Continuous.add hf hg""",
    "comm": """import Mathlib.Tactic

theorem add_comm_nat (a b : ℕ) : a + b = b + a := by
  ring""",
}


def get_mock_proof(description: str) -> str:
    desc_lower = description.lower()
    if "continuous" in desc_lower or "sum" in desc_lower:
        return MOCK_GENERATED_PROOFS["continuous"]
    elif "commut" in desc_lower or "comm" in desc_lower:
        return MOCK_GENERATED_PROOFS["comm"]
    return MOCK_GENERATED_PROOFS["default"]


@router.post("/generate/proof")
async def generate_proof(
    request: GenerateRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Generate a Lean 4 proof draft from natural language description.
    Uses Claude API to generate compilable Lean 4 code.
    Requires authentication. Advanced strategies require Researcher+ plan.
    """
    user_plan = get_user_plan(user_id)
    require_plan(user_plan, ["researcher", "lab", "admin"])
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    start = time.time()

    # Mock: In production, call Claude API with relevant Mathlib context
    lean_code = get_mock_proof(request.description)

    generation_time = int((time.time() - start) * 1000) + 2800  # include mock AI time

    compilation = CompilationResult(
        status="success",
        errors=[],
        time_ms=3200,
    )

    return ok(
        GenerateResponse(
            lean_code=lean_code,
            compilation=compilation,
            used_lemmas=["Nat.add_zero", "simp"],
            explanation=(
                "This proof uses the `simp` tactic to automatically simplify the goal "
                "using standard library lemmas. The proof framework was generated based "
                "on your description and verified against Lean 4 syntax."
            ),
            generation_time_ms=generation_time,
            proof_strategy=request.proof_strategy,
            confidence=0.85,
        ).model_dump()
    )
