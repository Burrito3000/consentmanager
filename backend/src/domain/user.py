"""User entity with RBAC for the admin portal.

Roles:
- OWNER: full access, can manage tenants and billing
- DPO: Data Protection Officer — can view audits, manage purposes, process rights
- ANALYST: read-only access to dashboards and reports
- AUDITOR: read-only access to audit logs and consent records
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .exceptions import InvalidConsentError


class UserRole(StrEnum):
    OWNER = "OWNER"
    DPO = "DPO"
    ANALYST = "ANALYST"
    AUDITOR = "AUDITOR"


# Role-based access matrix
ROLE_PERMISSIONS: dict[UserRole, set[str]] = {
    UserRole.OWNER: {
        "tenant.manage",
        "purpose.manage",
        "consent.view",
        "consent.manage",
        "audit.view",
        "rights.manage",
        "webhook.manage",
        "api_key.manage",
        "user.manage",
        "analytics.view",
        "settings.manage",
    },
    UserRole.DPO: {
        "purpose.view",
        "purpose.manage",
        "consent.view",
        "audit.view",
        "rights.manage",
        "grievance.manage",
        "notice.manage",
        "analytics.view",
    },
    UserRole.ANALYST: {
        "consent.view",
        "analytics.view",
        "purpose.view",
    },
    UserRole.AUDITOR: {
        "consent.view",
        "audit.view",
        "purpose.view",
    },
}


@dataclass(frozen=True)
class User:
    """An admin user with RBAC.

    Invariants:
    - email must be valid
    - password_hash must be non-empty
    - role must be a valid UserRole
    - tenant_id is required
    """

    tenant_id: str
    email: str
    password_hash: str
    role: UserRole = UserRole.ANALYST
    is_active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    last_login_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.email or "@" not in self.email:
            raise InvalidConsentError("Valid email is required")
        if not self.password_hash:
            raise InvalidConsentError("Password hash is required")
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")

    def has_permission(self, permission: str) -> bool:
        return permission in ROLE_PERMISSIONS.get(self.role, set())

    def change_role(self, new_role: UserRole) -> User:
        return User(
            id=self.id,
            tenant_id=self.tenant_id,
            email=self.email,
            password_hash=self.password_hash,
            role=new_role,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
            last_login_at=self.last_login_at,
        )

    def record_login(self) -> User:
        return User(
            id=self.id,
            tenant_id=self.tenant_id,
            email=self.email,
            password_hash=self.password_hash,
            role=self.role,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
            last_login_at=datetime.now(UTC),
        )
