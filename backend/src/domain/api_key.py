"""ApiKey entity — per-tenant API keys with origin allowlisting."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .exceptions import InvalidConsentError


@dataclass(frozen=True)
class ApiKey:
    """A tenant-scoped API key for SDK and server-to-server auth.

    Invariants:
    - key_prefix is used for identification (not the full key)
    - key_hash stores the bcrypt/argon2 hash
    - allowed_origins restricts CORS for SDK usage
    - is_active controls whether the key is usable
    """

    tenant_id: str
    key_prefix: str
    key_hash: str
    label: str
    allowed_origins: tuple[str, ...] = ()
    is_active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")
        if not self.key_prefix:
            raise InvalidConsentError("Key prefix is required")
        if not self.key_hash:
            raise InvalidConsentError("Key hash is required")
        if not self.label:
            raise InvalidConsentError("Label is required")

    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at

    def is_origin_allowed(self, origin: str) -> bool:
        if not self.allowed_origins:
            return True  # No restrictions
        return origin in self.allowed_origins

    def deactivate(self) -> ApiKey:
        return ApiKey(
            id=self.id,
            tenant_id=self.tenant_id,
            key_prefix=self.key_prefix,
            key_hash=self.key_hash,
            label=self.label,
            allowed_origins=self.allowed_origins,
            is_active=False,
            created_at=self.created_at,
            expires_at=self.expires_at,
        )
