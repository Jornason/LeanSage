"""
LeanProve AI - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.schemas.common import error as error_response, Meta
from app.routers import search, generate, diagnose, convert, compile, explain, auth, user, proof, billing

app = FastAPI(
    title="LeanProve AI API",
    description="AI-powered Lean 4 math proof assistant API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:3005"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# ---------------------------------------------------------------------------
# Global exception handlers for consistent error response format
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Wrap all HTTP exceptions in the standard {success, error, code, meta} format."""
    code_map = {
        400: "INVALID_INPUT",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        422: "VALIDATION_ERROR",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_ERROR",
        502: "UPSTREAM_ERROR",
    }
    error_code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    meta = Meta()
    body = {
        "success": False,
        "error": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        "code": error_code,
        "meta": meta.model_dump(),
    }
    headers = getattr(exc, "headers", None)
    return JSONResponse(status_code=exc.status_code, content=body, headers=headers)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Wrap Pydantic validation errors in the standard format."""
    meta = Meta()
    errors = exc.errors()
    detail = "; ".join(
        f"{'.'.join(str(loc) for loc in e.get('loc', []))}: {e.get('msg', '')}"
        for e in errors
    )
    body = {
        "success": False,
        "error": detail,
        "code": "VALIDATION_ERROR",
        "meta": meta.model_dump(),
    }
    return JSONResponse(status_code=422, content=body)


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/")
async def root():
    return {
        "message": "LeanProve AI API",
        "docs": "/docs",
        "version": "0.1.0",
    }


# Include routers with v1 prefix
PREFIX = "/v1"

app.include_router(auth.router, prefix=PREFIX, tags=["Authentication"])
app.include_router(search.router, prefix=PREFIX, tags=["Search"])
app.include_router(generate.router, prefix=PREFIX, tags=["Generation"])
app.include_router(diagnose.router, prefix=PREFIX, tags=["Diagnosis"])
app.include_router(convert.router, prefix=PREFIX, tags=["Conversion"])
app.include_router(compile.router, prefix=PREFIX, tags=["Compilation"])
app.include_router(explain.router, prefix=PREFIX, tags=["Explanation"])
app.include_router(user.router, prefix=PREFIX, tags=["User"])
app.include_router(proof.router, prefix=PREFIX, tags=["Proof Sessions"])
app.include_router(billing.router, prefix=PREFIX, tags=["Billing"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
