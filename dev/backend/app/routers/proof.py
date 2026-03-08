"""
Proof Sessions Router
GET    /v1/proof/sessions
POST   /v1/proof/sessions
GET    /v1/proof/sessions/{session_id}
PATCH  /v1/proof/sessions/{session_id}
DELETE /v1/proof/sessions/{session_id}
"""

import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.schemas.api import CreateSessionRequest, UpdateSessionRequest, ProofSessionResponse
from app.schemas.common import ok, paginated
from app.core.auth import get_current_user_id, get_user_plan, check_rate_limit

router = APIRouter()

# Mock session store (replace with database in production)
MOCK_SESSIONS: dict[str, dict] = {
    "session_1": {
        "id": "session_1",
        "user_id": "user_demo_123",
        "title": "Continuity of Sum",
        "description": "Prove sum of continuous functions is continuous",
        "current_code": "import Mathlib.Topology.Algebra.Group.Basic\n\ntheorem sum_continuous {f g : \u03b1 \u2192 \u03b2} [TopologicalSpace \u03b1] [TopologicalSpace \u03b2] [Add \u03b2] [ContinuousAdd \u03b2] (hf : Continuous f) (hg : Continuous g) : Continuous (fun x => f x + g x) := by\n  exact Continuous.add hf hg",
        "compilation_status": "success",
        "last_error": None,
        "created_at": "2026-03-05T10:00:00Z",
        "updated_at": "2026-03-07T08:00:00Z",
    },
    "session_2": {
        "id": "session_2",
        "user_id": "user_demo_123",
        "title": "Cauchy Sequences",
        "description": "Cauchy sequence convergence in complete metric spaces",
        "current_code": "import Mathlib.Tactic\n\ntheorem cauchy_conv (s : \u2115 \u2192 \u211d) (hs : IsCauSeq abs s) : \u2203 L : \u211d, Filter.Tendsto s Filter.atTop (nhds L) := by\n  sorry",
        "compilation_status": "error",
        "last_error": "use of 'sorry'",
        "created_at": "2026-03-04T14:00:00Z",
        "updated_at": "2026-03-06T15:00:00Z",
    },
    "session_3": {
        "id": "session_3",
        "user_id": "user_demo_123",
        "title": "IVT Proof",
        "description": "Intermediate Value Theorem formalization",
        "current_code": "import Mathlib.Topology.Order.IntermediateValue\n\nexample : \u2200 (f : \u211d \u2192 \u211d), Continuous f \u2192 \u2200 a b : \u211d, a < b \u2192 \u2200 y : \u211d, f a < y \u2192 y < f b \u2192 \u2203 x \u2208 Set.Ioo a b, f x = y := by\n  intro f hf a b hab y hya hyb\n  exact intermediate_value_Ioo hab hf.continuousOn \u27e8hya.le, hyb.le\u27e9",
        "compilation_status": "success",
        "last_error": None,
        "created_at": "2026-03-03T09:00:00Z",
        "updated_at": "2026-03-05T11:00:00Z",
    },
}


@router.get("/proof/sessions")
async def list_sessions(
    page: int = 1,
    per_page: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """List all proof sessions for the current user. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    user_sessions = [
        s for s in MOCK_SESSIONS.values() if s["user_id"] == user_id
    ]
    # Sort by updated_at desc
    user_sessions.sort(key=lambda s: s["updated_at"], reverse=True)

    total = len(user_sessions)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = user_sessions[start:end]

    return paginated(data=page_data, page=page, per_page=per_page, total=total)


@router.post("/proof/sessions")
async def create_session(
    request: CreateSessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Create a new proof session. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    session_id = f"session_{uuid.uuid4().hex[:8]}"
    now = datetime.utcnow().isoformat() + "Z"
    session = {
        "id": session_id,
        "user_id": user_id,
        "title": request.title,
        "description": request.description,
        "current_code": "import Mathlib.Tactic\n\n-- Start your proof here\n",
        "compilation_status": "pending",
        "last_error": None,
        "created_at": now,
        "updated_at": now,
    }
    MOCK_SESSIONS[session_id] = session
    return ok(session)


@router.get("/proof/sessions/{session_id}")
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Get a specific proof session. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    session = MOCK_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return ok(session)


@router.patch("/proof/sessions/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Update a proof session. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    session = MOCK_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    updates = request.model_dump(exclude_none=True)
    session.update(updates)
    session["updated_at"] = datetime.utcnow().isoformat() + "Z"
    return ok(session)


@router.delete("/proof/sessions/{session_id}")
async def delete_session(
    session_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Delete a proof session. Requires authentication."""
    user_plan = get_user_plan(user_id)
    check_rate_limit(user_id, user_plan)

    session = MOCK_SESSIONS.get(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    if session["user_id"] != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    del MOCK_SESSIONS[session_id]
    return ok({"deleted": session_id})
