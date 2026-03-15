"""
Pydantic schemas for all API endpoints
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# === Search ===

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    top_k: int = Field(default=5, ge=1, le=20)
    filter_module: Optional[str] = None


class TheoremResult(BaseModel):
    rank: int
    theorem_name: str
    full_name: str
    type_signature: str
    module: str
    doc_url: str
    similarity: float


class SearchResponse(BaseModel):
    results: List[TheoremResult]
    total_results: int = 0
    query_embedding_time_ms: int
    search_time_ms: int


# === Generation ===

class GenerateRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=2000)
    context: Optional[str] = None
    style: Literal["tactic", "term"] = "tactic"
    auto_compile: bool = True
    proof_strategy: Literal[
        "auto", "induction", "cases", "contradiction",
        "construction", "rewrite"
    ] = "auto"
    theorem_type: Literal[
        "theorem", "lemma", "example", "def", "instance"
    ] = "theorem"


class CompilationResult(BaseModel):
    status: Literal["success", "error", "timeout"]
    errors: List[str] = []
    time_ms: int


class GenerateResponse(BaseModel):
    lean_code: str
    compilation: CompilationResult
    used_lemmas: List[str]
    explanation: str
    generation_time_ms: int
    proof_strategy: str = "auto"
    confidence: float = 0.0


# === Diagnosis ===

class DiagnoseRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    error_message: Optional[str] = None
    severity_filter: Literal["all", "error", "warning", "info"] = "all"


class FixSuggestion(BaseModel):
    description: str
    fixed_code: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class DiagnosticItem(BaseModel):
    line: int
    column: int
    severity: Literal["error", "warning", "info"]
    original_error: str
    explanation: str
    suggestions: List[FixSuggestion]


class DiagnoseResponse(BaseModel):
    diagnostics: List[DiagnosticItem]
    total_errors: int = 0
    total_warnings: int = 0


# === Conversion ===

class LatexToLeanRequest(BaseModel):
    latex: str = Field(..., min_length=1, max_length=5000)
    include_imports: bool = False
    target_type: Literal["expression", "declaration", "tactic"] = "expression"


class LatexToLeanResponse(BaseModel):
    lean_expression: str
    lean_declaration: Optional[str] = None
    imports: List[str] = []
    conversion_notes: List[str] = []


class LeanToLatexRequest(BaseModel):
    lean_code: str = Field(..., min_length=1, max_length=5000)
    format: Literal["inline", "display"] = "display"


class LeanToLatexResponse(BaseModel):
    latex: str
    rendered_preview_url: Optional[str] = None


# === Compilation ===

class CompileRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=50000)
    timeout_seconds: int = Field(default=60, ge=1, le=120)
    lean_version: Literal["4.8.0", "4.7.0", "4.6.0", "latest"] = "latest"


class CompileCheckResponse(BaseModel):
    status: Literal["success", "error", "timeout"]
    errors: List[dict] = []
    warnings: List[dict] = []
    goals: List[dict] = []
    time_ms: int
    lean_version: str
    mathlib_version: str


# === Explanation ===

class ExplainRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=10000)
    language: Literal["zh", "en", "ja", "ko", "fr", "de"] = "en"
    detail_level: Literal["brief", "standard", "detailed"] = "standard"


class TacticStep(BaseModel):
    tactic: str
    explanation: str
    doc_url: Optional[str] = None


class ExplainResponse(BaseModel):
    steps: List[TacticStep]
    summary: str = ""
    language: str = "en"


# === Auth ===

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    display_name: str = Field(..., min_length=2, max_length=100)
    locale: Literal["en", "zh", "ja", "ko", "fr", "de"] = "en"


class UserInfo(BaseModel):
    id: str
    email: str
    display_name: str
    role: str
    avatar_url: Optional[str] = None
    locale: str = "en"
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 604800  # 7 days in seconds
    user: UserInfo


# === User ===

class UsageStats(BaseModel):
    used: int
    limit: int  # -1 for unlimited


class UsageResponse(BaseModel):
    plan: str
    period: str
    searches: UsageStats
    generations: UsageStats
    diagnoses: UsageStats
    compilations: UsageStats
    api_calls_today: int
    rate_limit: dict


# === Proof Sessions ===

class CreateSessionRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)


class UpdateSessionRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    current_code: Optional[str] = Field(default=None, max_length=100000)
    compilation_status: Optional[Literal["pending", "success", "error"]] = None


class ProofSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    current_code: Optional[str] = None
    compilation_status: Optional[str] = None
    last_error: Optional[str] = None
    created_at: str
    updated_at: str


# === Billing ===

class CreateCheckoutRequest(BaseModel):
    plan: Literal["researcher", "lab", "enterprise"] = "researcher"
    billing_cycle: Literal["monthly", "annual"] = "monthly"


class SubscriptionResponse(BaseModel):
    plan: str
    status: Literal["active", "canceled", "past_due"] = "active"
    current_period_start: Optional[str] = None
    current_period_end: Optional[str] = None
    cancel_at_period_end: bool = False
