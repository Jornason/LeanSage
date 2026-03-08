"""
Error Diagnosis Router
POST /v1/diagnose/error
"""

import re
from typing import Optional
from fastapi import APIRouter, Depends

from app.schemas.api import DiagnoseRequest, DiagnoseResponse, DiagnosticItem, FixSuggestion
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota,
)

router = APIRouter()


def analyze_error(code: str, error_message: Optional[str]) -> list[DiagnosticItem]:
    """
    Mock error analysis. In production, calls Claude API with code + error context.
    """
    diagnostics = []

    if error_message:
        # Parse line number from error if available
        line_match = re.search(r":(\d+):", error_message)
        line = int(line_match.group(1)) if line_match else 1

        # Map common Lean 4 errors to explanations
        if "unknown tactic" in error_message:
            tactic_match = re.search(r"unknown tactic '(.+?)'", error_message)
            tactic = tactic_match.group(1) if tactic_match else "unknown"
            correct_tactic = tactic.rstrip("_bad").rstrip("_wrong") if "_" in tactic else "omega"

            diagnostics.append(DiagnosticItem(
                line=line,
                column=2,
                severity="error",
                original_error=error_message,
                explanation=(
                    f"Lean 4 does not have a tactic named '{tactic}'. "
                    f"You may have meant '{correct_tactic}', which is a valid Lean 4 tactic. "
                    f"The '{correct_tactic}' tactic can automatically solve linear arithmetic goals."
                ),
                suggestions=[
                    FixSuggestion(
                        description=f"Replace '{tactic}' with '{correct_tactic}'",
                        fixed_code=code.replace(tactic, correct_tactic),
                        confidence=0.95,
                    )
                ],
            ))
        elif "type mismatch" in error_message:
            diagnostics.append(DiagnosticItem(
                line=line,
                column=1,
                severity="error",
                original_error=error_message,
                explanation=(
                    "There is a type mismatch in your proof. Lean 4 expected one type "
                    "but received another. Check that the types of all variables and "
                    "expressions are consistent with the theorem statement."
                ),
                suggestions=[
                    FixSuggestion(
                        description="Add explicit type annotation to clarify the type",
                        fixed_code=code,
                        confidence=0.6,
                    )
                ],
            ))
        elif "unknown identifier" in error_message:
            id_match = re.search(r"unknown identifier '(.+?)'", error_message)
            identifier = id_match.group(1) if id_match else "unknown"
            diagnostics.append(DiagnosticItem(
                line=line,
                column=1,
                severity="error",
                original_error=error_message,
                explanation=(
                    f"The identifier '{identifier}' is not in scope. Make sure you have "
                    f"imported the correct Mathlib module or check the spelling of the lemma name."
                ),
                suggestions=[
                    FixSuggestion(
                        description=f"Add 'import Mathlib.Tactic' or the specific module",
                        fixed_code=f"import Mathlib.Tactic\n\n{code}",
                        confidence=0.75,
                    )
                ],
            ))
        else:
            # Generic error
            diagnostics.append(DiagnosticItem(
                line=line,
                column=1,
                severity="error",
                original_error=error_message,
                explanation=(
                    "The Lean 4 compiler encountered an error. This may be due to a "
                    "syntax error, type mismatch, or missing import. Review the code "
                    "near the indicated line and ensure all types are correct."
                ),
                suggestions=[],
            ))
    else:
        # No error provided -- check code heuristically
        if "sorry" in code:
            sorry_lines = [i + 1 for i, l in enumerate(code.split("\n")) if "sorry" in l]
            for sorry_line in sorry_lines:
                diagnostics.append(DiagnosticItem(
                    line=sorry_line,
                    column=1,
                    severity="warning",
                    original_error="use of 'sorry'",
                    explanation=(
                        "Your proof contains 'sorry', which is a placeholder that allows "
                        "Lean to accept incomplete proofs. Replace 'sorry' with actual "
                        "proof steps to complete your theorem."
                    ),
                    suggestions=[],
                ))

    return diagnostics


@router.post("/diagnose/error")
async def diagnose_error(
    request: DiagnoseRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Diagnose compilation errors in Lean 4 code.
    Returns AI-powered explanations and fix suggestions.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    diagnostics = analyze_error(request.code, request.error_message)

    # Apply severity filter if not "all"
    if request.severity_filter != "all":
        diagnostics = [d for d in diagnostics if d.severity == request.severity_filter]

    total_errors = sum(1 for d in diagnostics if d.severity == "error")
    total_warnings = sum(1 for d in diagnostics if d.severity == "warning")

    return ok(
        DiagnoseResponse(
            diagnostics=diagnostics,
            total_errors=total_errors,
            total_warnings=total_warnings,
        ).model_dump()
    )
