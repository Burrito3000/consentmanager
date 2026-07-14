"""DataPrincipal entity — the end-user whose consent is managed."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .exceptions import InvalidConsentError


@dataclass(frozen=True)
class DataPrincipal:
    """A Data Principal (end-user) whose consent is tracked.

    Stores only a reference to the tenant's user identifier.
    No raw personal data is stored here (data minimization).

    Invariants:
    - external_ref must be non-empty (the tenant's user ID)
    - email, if provided, must contain '@'
    """

    tenant_id: str
    external_ref: str
    email: str | None = None
    phone: str | None = None
    locale: str = "en"
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.external_ref:
            raise InvalidConsentError("External reference is required")
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")
        if self.email and "@" not in self.email:
            raise InvalidConsentError("Invalid email format")
