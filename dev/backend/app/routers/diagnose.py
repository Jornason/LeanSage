"""
Error Diagnosis Router
POST /v1/diagnose/error
"""

import re
import json
from typing import Optional
from fastapi import APIRouter, Depends

from app.schemas.api import DiagnoseRequest, DiagnoseResponse, DiagnosticItem, FixSuggestion
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota,
)
from app.core.ai_client import chat

router = APIRouter()

_SYSTEM_PROMPT = """\
You are an expert Lean 4 debugger. Analyze Lean 4 code and compiler errors.
Respond with ONLY a JSON object (no markdown, no extra text) in this exact shape:
{
  "diagnostics": [
    {
      "line": <int, 1-based line number>,
      "column": <int>,
      "severity": "error" | "warning",
      "explanation": "<plain-language explanation of the error>",
      "suggestion": "<description of the fix>",
      "fixed_code": "<the corrected Lean 4 code>",
      "confidence": <float 0-1>
    }
  ]
}
If no errors, return {"diagnostics": []}.
"""


def _parse_ai_diagnostics(ai_text: str, code: str) -> list[DiagnosticItem]:
    """Parse JSON from AI response into DiagnosticItem list."""
    try:
        # Strip any accidental markdown fences
        text = re.sub(r"```(?:json)?\s*", "", ai_text).strip().rstrip("`").strip()
        data = json.loads(text)
        items = []
        for d in data.get("diagnostics", []):
            items.append(DiagnosticItem(
                line=int(d.get("line", 1)),
                column=int(d.get("column", 1)),
                severity=d.get("severity", "error"),
                original_error=d.get("explanation", ""),
                explanation=d.get("explanation", ""),
                suggestions=[FixSuggestion(
                    description=d.get("suggestion", ""),
                    fixed_code=d.get("fixed_code", code),
                    confidence=float(d.get("confidence", 0.7)),
                )] if d.get("suggestion") else [],
            ))
        return items
    except Exception:
        return []


def _heuristic_diagnostics(code: str, error_message: Optional[str]) -> list[DiagnosticItem]:
    """Regex-based fallback when AI is unavailable."""
    diagnostics = []
    if error_message:
        line_match = re.search(r":(\d+):", error_message)
        line = int(line_match.group(1)) if line_match else 1

        if "unknown tactic" in error_message:
            tactic_match = re.search(r"unknown tactic '(.+?)'", error_message)
            tactic = tactic_match.group(1) if tactic_match else "unknown"
            correct = tactic.rstrip("_bad").rstrip("_wrong") if "_" in tactic else "omega"
            diagnostics.append(DiagnosticItem(
                line=line, column=2, severity="error",
                original_error=error_message,
                explanation=(
                    f"Lean 4 does not have a tactic named '{tactic}'. "
                    f"You may have meant '{correct}'."
                ),
                suggestions=[FixSuggestion(
                    description=f"Replace '{tactic}' with '{correct}'",
                    fixed_code=code.replace(tactic, correct),
                    confidence=0.95,
                )],
            ))
        elif "type mismatch" in error_message:
            diagnostics.append(DiagnosticItem(
                line=line, column=1, severity="error",
                original_error=error_message,
                explanation="Type mismatch: check that all variables and expressions use consistent types.",
                suggestions=[FixSuggestion(
                    description="Add explicit type annotation to clarify the type",
                    fixed_code=code, confidence=0.6,
                )],
            ))
        elif "unknown identifier" in error_message:
            id_match = re.search(r"unknown identifier '(.+?)'", error_message)
            identifier = id_match.group(1) if id_match else "unknown"
            diagnostics.append(DiagnosticItem(
                line=line, column=1, severity="error",
                original_error=error_message,
                explanation=f"'{identifier}' is not in scope. Check imports or spelling.",
                suggestions=[FixSuggestion(
                    description="Add 'import Mathlib.Tactic' or the specific module",
                    fixed_code=f"import Mathlib.Tactic\n\n{code}",
                    confidence=0.75,
                )],
            ))
        else:
            diagnostics.append(DiagnosticItem(
                line=line, column=1, severity="error",
                original_error=error_message,
                explanation="Lean 4 compiler error. Review the code near the indicated line.",
                suggestions=[],
            ))
    else:
        if "sorry" in code:
            for i, line_text in enumerate(code.split("\n"), 1):
                if "sorry" in line_text:
                    diagnostics.append(DiagnosticItem(
                        line=i, column=1, severity="warning",
                        original_error="use of 'sorry'",
                        explanation="'sorry' is a placeholder — replace it with a real proof.",
                        suggestions=[],
                    ))
    return diagnostics


@router.post("/diagnose/error")
async def diagnose_error(
    request: DiagnoseRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Diagnose compilation errors in Lean 4 code using aws-gpt-5.4.
    Falls back to heuristic analysis if AI is unavailable.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    # Build AI prompt
    user_prompt = f"Lean 4 code:\n```lean\n{request.code}\n```"
    if request.error_message:
        user_prompt += f"\n\nCompiler error message:\n{request.error_message}"
    else:
        user_prompt += "\n\nNo compiler error provided — check the code for issues."

    ai_text = chat(system=_SYSTEM_PROMPT, user=user_prompt, temperature=0.1, max_tokens=1024)

    if ai_text:
        diagnostics = _parse_ai_diagnostics(ai_text, request.code)
        # If JSON parse failed, fall back to heuristics
        if not diagnostics and request.error_message:
            diagnostics = _heuristic_diagnostics(request.code, request.error_message)
    else:
        diagnostics = _heuristic_diagnostics(request.code, request.error_message)

    if request.severity_filter != "all":
        diagnostics = [d for d in diagnostics if d.severity == request.severity_filter]

    total_errors = sum(1 for d in diagnostics if d.severity == "error")
    total_warnings = sum(1 for d in diagnostics if d.severity == "warning")

    return ok(DiagnoseResponse(
        diagnostics=diagnostics,
        total_errors=total_errors,
        total_warnings=total_warnings,
    ).model_dump())
