"""Authentication and authorization for the FastAPI public API.

Uses per-tenant API keys for server-to-server and JWT for SDK tokens.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.settings import settings

security = HTTPBearer(auto_error=False)


def verify_api_key(
    request: Request,
    x_api_key: str | None = Header(None),
) -> str:
    """Verify X-API-Key header and extract tenant_id.

    In production, this checks against the DB. For now, validates format.
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    # Key format: cmp_live_<prefix>_<secret>
    # In production, look up by prefix and verify hash
    if not x_api_key.startswith("cmp_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key format",
        )

    # TODO: Look up key in DB, verify hash, extract tenant_id
    # For now, extract tenant from key format: cmp_test_<tenant_id>
    parts = x_api_key.split("_")
    if len(parts) >= 3:
        return parts[2]  # tenant_id placeholder

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API key",
    )


def create_sdk_token(
    tenant_id: str,
    principal_ref: str,
    allowed_origins: list[str] | None = None,
) -> str:
    """Create a short-lived JWT for SDK usage.

    Tokens are scoped to a tenant + principal, with a short TTL (15 min).
    """
    now = datetime.now(UTC)
    payload = {
        "sub": principal_ref,
        "tenant_id": tenant_id,
        "iat": now,
        "exp": now + timedelta(minutes=settings.sdk_token_ttl_minutes),
        "type": "sdk",
        "origins": allowed_origins or [],
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_sdk_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Verify a JWT SDK token and return its payload."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "sdk":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid token type",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def verify_origin(
    request: Request,
    allowed_origins: list[str],
) -> None:
    """Verify that the request origin is in the allowed list for CORS."""
    origin = request.headers.get("origin", "")
    if allowed_origins and origin and origin not in allowed_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Origin not allowed",
        )


def get_tenant_id_from_token(
    payload: dict = Depends(verify_sdk_token),
) -> str:
    return payload["tenant_id"]


def get_principal_ref_from_token(
    payload: dict = Depends(verify_sdk_token),
) -> str:
    return payload["sub"]
