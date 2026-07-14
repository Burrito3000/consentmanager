"""Tenant (Data Fiduciary) entity — the top-level multi-tenant boundary."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .exceptions import InvalidTenantError


@dataclass(frozen=True)
class Tenant:
    """A Data Fiduciary that collects and processes consent.

    Invariants:
    - name must be non-empty
    - contact_email must be non-empty
    - at least one language in supported_languages
    - is_active must be boolean
    """

    name: str
    contact_email: str
    supported_languages: tuple[str, ...] = ("en",)
    is_active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidTenantError("Tenant name must not be empty")
        if not self.contact_email or "@" not in self.contact_email:
            raise InvalidTenantError("A valid contact email is required")
        if not self.supported_languages:
            raise InvalidTenantError("At least one supported language is required")

    def deactivate(self) -> Tenant:
        return Tenant(
            id=self.id,
            name=self.name,
            contact_email=self.contact_email,
            supported_languages=self.supported_languages,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )

    def update_languages(self, languages: list[str]) -> Tenant:
        if not languages:
            raise InvalidTenantError("At least one language must be supported")
        return Tenant(
            id=self.id,
            name=self.name,
            contact_email=self.contact_email,
            supported_languages=tuple(languages),
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )
