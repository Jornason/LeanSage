"""
LaTeX <-> Lean Conversion Router
POST /v1/convert/latex-to-lean
POST /v1/convert/lean-to-latex
"""

import re
from fastapi import APIRouter, Depends

from app.schemas.api import (
    LatexToLeanRequest, LatexToLeanResponse,
    LeanToLatexRequest, LeanToLatexResponse,
)
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota,
)

router = APIRouter()

# LaTeX -> Lean symbol mapping
LATEX_TO_LEAN_MAP = {
    r"\\forall": "\u2200",
    r"\\exists": "\u2203",
    r"\\in": "\u2208",
    r"\\notin": "\u2209",
    r"\\subset": "\u2282",
    r"\\subseteq": "\u2286",
    r"\\cup": "\u222a",
    r"\\cap": "\u2229",
    r"\\emptyset": "\u2205",
    r"\\mathbb\{N\}": "\u2115",
    r"\\mathbb\{Z\}": "\u2124",
    r"\\mathbb\{Q\}": "\u211a",
    r"\\mathbb\{R\}": "\u211d",
    r"\\mathbb\{C\}": "\u2102",
    r"\\alpha": "\u03b1",
    r"\\beta": "\u03b2",
    r"\\gamma": "\u03b3",
    r"\\delta": "\u03b4",
    r"\\epsilon": "\u03b5",
    r"\\lambda": "\u03bb",
    r"\\mu": "\u03bc",
    r"\\pi": "\u03c0",
    r"\\sigma": "\u03c3",
    r"\\tau": "\u03c4",
    r"\\phi": "\u03c6",
    r"\\psi": "\u03c8",
    r"\\omega": "\u03c9",
    r"\\to": "\u2192",
    r"\\rightarrow": "\u2192",
    r"\\leftarrow": "\u2190",
    r"\\leftrightarrow": "\u2194",
    r"\\iff": "\u2194",
    r"\\implies": "\u2192",
    r"\\land": "\u2227",
    r"\\lor": "\u2228",
    r"\\neg": "\u00ac",
    r"\\lnot": "\u00ac",
    r"\\geq": "\u2265",
    r"\\leq": "\u2264",
    r"\\neq": "\u2260",
    r"\\infty": "\u221e",
    r"\\sum": "\u2211",
    r"\\prod": "\u220f",
    r"\\int": "\u222b",
    r"\\partial": "\u2202",
    r"\\nabla": "\u2207",
    r"\\times": "\u00d7",
    r"\\cdot": "\u00b7",
    r"\\circ": "\u2218",
}

# Lean -> LaTeX symbol mapping (reverse)
LEAN_TO_LATEX_MAP = {v: k.replace("\\\\", "\\") for k, v in LATEX_TO_LEAN_MAP.items()}


def latex_to_lean_convert(latex: str) -> tuple[str, list[str], list[str]]:
    """Convert LaTeX expression to Lean 4 syntax. Returns (result, imports, notes)."""
    result = latex
    conversion_notes = []
    for pattern, replacement in LATEX_TO_LEAN_MAP.items():
        if re.search(pattern, result):
            result = re.sub(pattern, replacement, result)

    # Clean up remaining LaTeX artifacts
    result = re.sub(r"\\{", "(", result)
    result = re.sub(r"\\}", ")", result)
    result = re.sub(r"\{([^}]+)\}", r"\1", result)
    result = re.sub(r"_\{?(\w+)\}?", r"_\1", result)
    result = re.sub(r"\^(\w+)", r"^\1", result)
    result = re.sub(r"\\text\{([^}]+)\}", r"\1", result)

    # Check for unconverted LaTeX commands
    remaining = re.findall(r"\\[a-zA-Z]+", result)
    if remaining:
        conversion_notes.append(
            f"Some LaTeX commands could not be converted automatically: {', '.join(set(remaining))}"
        )

    imports = []
    if "\u2115" in result or "\u2124" in result:
        imports.append("import Mathlib.Data.Nat.Basic")
    if "\u211d" in result or "\u2102" in result:
        imports.append("import Mathlib.Analysis.SpecificLimits.Basic")
    if "\u2200" in result or "\u2203" in result:
        imports.append("import Mathlib.Tactic")

    return result.strip(), list(set(imports)), conversion_notes


def lean_to_latex_convert(lean: str) -> str:
    """Convert Lean 4 syntax to LaTeX."""
    result = lean
    for symbol, latex in LEAN_TO_LATEX_MAP.items():
        result = result.replace(symbol, f" {latex} ")

    # Clean up extra spaces
    result = re.sub(r"\s+", " ", result).strip()
    return result


@router.post("/convert/latex-to-lean")
async def convert_latex_to_lean(
    request: LatexToLeanRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Convert LaTeX mathematical expression to Lean 4 syntax.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    lean_expr, imports, notes = latex_to_lean_convert(request.latex)

    # Generate a declaration if it looks like a proposition
    lean_declaration = None
    if "\u2200" in lean_expr or "\u2203" in lean_expr or "\u2192" in lean_expr:
        lean_declaration = f"def converted_proposition : Prop :=\n  {lean_expr}"

    response = LatexToLeanResponse(
        lean_expression=lean_expr,
        lean_declaration=lean_declaration,
        imports=imports if request.include_imports else [],
        conversion_notes=notes,
    )
    return ok(response.model_dump())


@router.post("/convert/lean-to-latex")
async def convert_lean_to_latex(
    request: LeanToLatexRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Convert Lean 4 expression to LaTeX mathematical notation.
    Requires authentication.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    latex = lean_to_latex_convert(request.lean_code)

    response = LeanToLatexResponse(
        latex=latex,
        rendered_preview_url=None,  # Would be generated server-side in production
    )
    return ok(response.model_dump())
