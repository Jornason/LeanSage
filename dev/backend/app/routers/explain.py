"""
Tactic Explanation Router
POST /v1/explain/tactics
"""

from fastapi import APIRouter, Depends

from app.schemas.api import ExplainRequest, ExplainResponse, TacticStep
from app.schemas.common import ok
from app.core.auth import (
    get_current_user_id, get_user_plan,
    check_rate_limit, check_and_increment_quota, require_plan,
)
from app.core.ai_client import chat

router = APIRouter()

TACTIC_EXPLANATIONS_EN = {
    "ring": "The `ring` tactic proves goals that follow from the axioms of a commutative (semi)ring, such as commutativity and distributivity of addition and multiplication.",
    "simp": "The `simp` tactic simplifies the goal by rewriting with a collection of lemmas marked @[simp]. It can close many routine goals automatically.",
    "omega": "The `omega` tactic automatically solves linear arithmetic goals over integers and natural numbers, such as n + 1 > n.",
    "linarith": "The `linarith` tactic proves goals by linear arithmetic, combining given hypotheses using linear combinations.",
    "exact": "The `exact` tactic closes the goal if the provided term has exactly the same type as the goal.",
    "apply": "The `apply` tactic unifies the goal with the conclusion of a given theorem, creating new subgoals for each premise.",
    "intro": "The `intro` tactic introduces hypotheses from the goal. For `\u2200 x, P x`, it introduces `x : T` into the context.",
    "induction": "The `induction` tactic performs induction on a variable. It creates subgoals for each constructor of the inductive type.",
    "cases": "The `cases` tactic performs case analysis on a hypothesis or expression, splitting into subgoals for each constructor.",
    "constructor": "The `constructor` tactic applies the unique constructor of a structure or inductive type with exactly one constructor.",
    "norm_num": "The `norm_num` tactic normalizes numerical expressions and can prove numerical goals like 2 + 2 = 4.",
    "field_simp": "The `field_simp` tactic simplifies expressions involving division and field operations.",
    "push_neg": "The `push_neg` tactic pushes negations inside quantifiers and logical connectives.",
    "contrapose": "The `contrapose` tactic replaces the goal with its contrapositive.",
    "rw": "The `rw` (rewrite) tactic rewrites the goal using an equality or iff lemma.",
    "have": "The `have` tactic introduces an intermediate lemma with a given proof, adding it to the context.",
    "use": "The `use` tactic provides a witness for an existential goal.",
    "tauto": "The `tauto` tactic proves propositional tautologies automatically.",
    "decide": "The `decide` tactic proves decidable propositions by computation.",
    "sorry": "The `sorry` tactic is a placeholder that accepts any goal without proof. It should be replaced with real proofs.",
}

TACTIC_EXPLANATIONS_ZH = {
    "ring": "`ring` tactic \u7528\u4e8e\u8bc1\u660e\u4ea4\u6362\uff08\u534a\uff09\u73af\u516c\u7406\u5bfc\u51fa\u7684\u7b49\u5f0f\u76ee\u6807\uff0c\u4f8b\u5982\u52a0\u6cd5\u7684\u4ea4\u6362\u5f8b\u548c\u5206\u914d\u5f8b\u3002",
    "simp": "`simp` tactic \u4f7f\u7528\u6807\u6ce8\u4e86 @[simp] \u7684\u5f15\u7406\u96c6\u5408\u5316\u7b80\u76ee\u6807\uff0c\u53ef\u81ea\u52a8\u5173\u95ed\u8bb8\u591a\u5e38\u89c4\u76ee\u6807\u3002",
    "omega": "`omega` tactic \u81ea\u52a8\u6c42\u89e3\u6574\u6570\u548c\u81ea\u7136\u6570\u4e0a\u7684\u7ebf\u6027\u7b97\u672f\u76ee\u6807\uff0c\u4f8b\u5982 n + 1 > n\u3002",
    "linarith": "`linarith` tactic \u901a\u8fc7\u7ebf\u6027\u7b97\u672f\u8bc1\u660e\u76ee\u6807\uff0c\u5c06\u5df2\u77e5\u5047\u8bbe\u8fdb\u884c\u7ebf\u6027\u7ec4\u5408\u3002",
    "exact": "`exact` tactic \u5f53\u63d0\u4f9b\u7684\u9879\u4e0e\u76ee\u6807\u7c7b\u578b\u5b8c\u5168\u76f8\u540c\u65f6\u5173\u95ed\u76ee\u6807\u3002",
    "apply": "`apply` tactic \u5c06\u76ee\u6807\u4e0e\u7ed9\u5b9a\u5b9a\u7406\u7684\u7ed3\u8bba\u7edf\u4e00\uff0c\u4e3a\u6bcf\u4e2a\u524d\u63d0\u521b\u5efa\u65b0\u5b50\u76ee\u6807\u3002",
    "intro": "`intro` tactic \u4ece\u76ee\u6807\u4e2d\u5f15\u5165\u5047\u8bbe\u3002\u5bf9\u4e8e `\u2200 x, P x`\uff0c\u5c06 `x : T` \u5f15\u5165\u4e0a\u4e0b\u6587\u3002",
    "induction": "`induction` tactic \u5bf9\u53d8\u91cf\u8fdb\u884c\u5f52\u7eb3\uff0c\u4e3a\u5f52\u7eb3\u7c7b\u578b\u7684\u6bcf\u4e2a\u6784\u9020\u5b50\u521b\u5efa\u5b50\u76ee\u6807\u3002",
    "cases": "`cases` tactic \u5bf9\u5047\u8bbe\u6216\u8868\u8fbe\u5f0f\u8fdb\u884c\u60c5\u5f62\u5206\u6790\uff0c\u4e3a\u6bcf\u4e2a\u6784\u9020\u5b50\u5206\u62c6\u5b50\u76ee\u6807\u3002",
    "norm_num": "`norm_num` tactic \u89c4\u8303\u5316\u6570\u503c\u8868\u8fbe\u5f0f\uff0c\u53ef\u8bc1\u660e\u5982 2 + 2 = 4 \u7b49\u6570\u503c\u76ee\u6807\u3002",
    "rw": "`rw`\uff08rewrite\uff09tactic \u4f7f\u7528\u7b49\u5f0f\u6216 iff \u5f15\u7406\u6539\u5199\u76ee\u6807\u3002",
    "sorry": "`sorry` tactic \u662f\u5360\u4f4d\u7b26\uff0c\u53ef\u63a5\u53d7\u4efb\u4f55\u76ee\u6807\u800c\u65e0\u9700\u8bc1\u660e\u3002\u5e94\u66ff\u6362\u4e3a\u771f\u5b9e\u8bc1\u660e\u3002",
}

TACTIC_DOC_URLS = {
    "ring": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/Ring.html",
    "simp": "https://leanprover-community.github.io/mathlib4_docs/Init/Tactics.html#simp",
    "omega": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/Omega.html",
    "linarith": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/Linarith.html",
    "norm_num": "https://leanprover-community.github.io/mathlib4_docs/Mathlib/Tactic/NormNum.html",
}


def parse_tactics(code: str) -> list[str]:
    """Extract tactic names from Lean 4 proof code."""
    tactics = []
    in_proof = False
    for line in code.split("\n"):
        stripped = line.strip()
        if stripped.startswith("by"):
            in_proof = True
        if in_proof and stripped and not stripped.startswith("--"):
            # Extract tactic name (first word)
            tactic = stripped.split()[0].rstrip("!")
            if tactic and tactic not in ("by", "|", "\u00b7", "_"):
                tactics.append(tactic)
    return tactics


@router.post("/explain/tactics")
async def explain_tactics(
    request: ExplainRequest,
    user_id: str = Depends(get_current_user_id),
):
    """
    Explain Lean 4 tactics in plain language (supports multiple languages).
    Requires authentication. Detailed explanations require Researcher+ plan.
    """
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)
    check_and_increment_quota(user_id, user_plan)

    # Detailed explanations require Researcher+ plan
    if request.detail_level == "detailed":
        require_plan(user_plan, ["researcher", "lab", "admin"])

    tactics = parse_tactics(request.code)
    explanations = (
        TACTIC_EXPLANATIONS_ZH if request.language == "zh" else TACTIC_EXPLANATIONS_EN
    )

    steps = []
    lang_label = "Chinese" if request.language == "zh" else "English"
    for tactic in tactics:
        explanation = explanations.get(tactic)
        if explanation is None:
            # Unknown tactic — ask the AI
            ai_result = chat(
                system=(
                    "You are an expert Lean 4 educator. "
                    "Explain Lean 4 tactics concisely (1-2 sentences). "
                    f"Respond in {lang_label}. Return plain text only, no markdown."
                ),
                user=f"Explain the Lean 4 tactic: `{tactic}`",
                temperature=0.3,
                max_tokens=200,
            )
            explanation = ai_result.strip() if ai_result else (
                f"The `{tactic}` tactic is used in this proof step. "
                "Refer to the Lean 4 documentation for details."
            )
        doc_url = TACTIC_DOC_URLS.get(tactic)
        steps.append(TacticStep(tactic=tactic, explanation=explanation, doc_url=doc_url))

    if not steps:
        steps.append(TacticStep(
            tactic="(no tactics found)",
            explanation="No tactic proof steps were detected. Make sure your code uses 'by' followed by tactics.",
            doc_url=None,
        ))

    # Build summary
    tactic_names = [s.tactic for s in steps if s.tactic != "(no tactics found)"]
    summary = (
        f"Found {len(tactic_names)} tactic(s): {', '.join(tactic_names)}"
        if tactic_names
        else "No tactics detected in the provided code."
    )

    return ok(
        ExplainResponse(
            steps=steps,
            summary=summary,
            language=request.language,
        ).model_dump()
    )
