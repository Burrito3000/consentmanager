"""FastAPI application — public API for the DPDP Consent Management Platform."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes.admin import router as admin_router
from src.api.routes.consent import router as consent_router
from src.api.routes.rights import router as rights_router
from src.api.schemas import HealthResponse
from src.config.settings import settings
from src.domain.exceptions import DomainError

logger = structlog.get_logger()

app = FastAPI(
    title="DPDP Consent Management Platform API",
    description=(
        "Public API for managing end-user consent under India's DPDP Act 2023.\n\n"
        "## DPDP Compliance\n"
        "- Per-purpose granular consent (no bundling)\n"
        "- Explicit affirmative action required\n"
        "- Withdrawal as easy as grant\n"
        "- Append-only event log with tamper-evident audit chain\n"
        "- Multilingual notices (English + Indian languages)\n"
        "- Rights request and grievance workflows with SLA timers\n"
        "- Data minimization: consent metadata only"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "CMP Support",
        "email": "support@cmp.example.com",
    },
    license_info={
        "name": "Proprietary",
    },
)

# CORS — will be locked to tenant-registered origins in production
origins = settings.cors_origins.split(",") if settings.cors_origins else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
    logger.warning("domain_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_code": exc.__class__.__name__},
    )


@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_error", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Include routers
app.include_router(admin_router, prefix="/api/v1")
app.include_router(consent_router, prefix="/api/v1")
app.include_router(rights_router, prefix="/api/v1")


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", version="1.0.0")


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "service": "DPDP Consent Management Platform",
        "version": "1.0.0",
        "docs": "/docs",
    }
