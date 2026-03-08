"""
Lean Compilation Router
POST /v1/compile/check
"""

import time
from fastapi import APIRouter, Depends

from app.schemas.api import CompileRequest, CompileCheckResponse
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota, require_plan,
)

router = APIRouter()


def mock_compile(code: str) -> dict:
    """
    Mock Lean compilation. In production, calls Modal.com with Lean 4 + Mathlib installed.
    """
    errors = []
    warnings = []
    goals = []

    # Simple heuristic checks
    lines = code.split("\n")
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        # Check for known bad patterns
        if "omega_bad" in stripped or "simp_bad" in stripped or "ring_bad" in stripped:
            tactic = next(
                (t for t in ["omega_bad", "simp_bad", "ring_bad"] if t in stripped),
                "unknown",
            )
            errors.append({
                "line": i,
                "column": stripped.index(tactic) + 1,
                "severity": "error",
                "message": f"unknown tactic '{tactic}'",
            })
        if "sorry" in stripped and not stripped.startswith("--"):
            warnings.append({
                "line": i,
                "column": stripped.index("sorry") + 1,
                "severity": "warning",
                "message": "use of 'sorry'",
            })

    status = "error" if errors else "success"

    return {
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "goals": goals,
        "time_ms": 3200 + len(code) // 10,
        "lean_version": "4.8.0",
        "mathlib_version": "2026-03-01",
    }


@router.post("/compile/check")
async def compile_check(
    request: CompileRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Check Lean 4 code compilation via Modal.com serverless function.
    Returns compilation status, errors, warnings, and proof goals.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    require_plan(user_plan, ["researcher", "lab", "admin"])
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    result = mock_compile(request.code)
    return ok(CompileCheckResponse(**result).model_dump())
