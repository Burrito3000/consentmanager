"""Purpose entity — each data-collection purpose with granular consent."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .exceptions import InvalidPurposeError


class LawfulBasis(StrEnum):
    CONSENT = "consent"
    LEGAL_OBLIGATION = "legal_obligation"
    CONTRACT = "contract"
    VITAL_INTEREST = "vital_interest"
    PUBLIC_INTEREST = "public_interest"
    LEGITIMATE_INTEREST = "legitimate_interest"


@dataclass(frozen=True)
class Purpose:
    """A data-collection purpose requiring separate consent.

    Invariants (DPDP §4-6):
    - name is non-empty
    - description is non-empty
    - data_categories must contain at least one item
    - retention_period_days > 0
    - is_mandatory purposes must still have individual toggle (no bundling)
    - lawful_basis must be a valid LawfulBasis
    """

    tenant_id: str
    name: str
    description: str
    data_categories: tuple[str, ...]
    retention_period_days: int
    lawful_basis: LawfulBasis = LawfulBasis.CONSENT
    is_mandatory: bool = False
    is_active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.name or not self.name.strip():
            raise InvalidPurposeError("Purpose name must not be empty")
        if not self.description or not self.description.strip():
            raise InvalidPurposeError("Purpose description must not be empty")
        if not self.data_categories:
            raise InvalidPurposeError("At least one data category is required")
        if self.retention_period_days < 1:
            raise InvalidPurposeError("Retention period must be >= 1 day")
        if not self.tenant_id:
            raise InvalidPurposeError("Tenant ID is required")
        # DPDP: mandatory purposes still require individual notice and toggle
        # (enforced at consent-grant time, not here)

    def with_version(self, new_version: int) -> Purpose:
        return Purpose(
            id=self.id,
            tenant_id=self.tenant_id,
            name=self.name,
            description=self.description,
            data_categories=self.data_categories,
            retention_period_days=self.retention_period_days,
            lawful_basis=self.lawful_basis,
            is_mandatory=self.is_mandatory,
            is_active=self.is_active,
            version=new_version,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )

    def deactivate(self) -> Purpose:
        return Purpose(
            id=self.id,
            tenant_id=self.tenant_id,
            name=self.name,
            description=self.description,
            data_categories=self.data_categories,
            retention_period_days=self.retention_period_days,
            lawful_basis=self.lawful_basis,
            is_mandatory=self.is_mandatory,
            is_active=False,
            version=self.version,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )
