"""Audit service — tamper-evident logging with hash chain."""

from __future__ import annotations

from typing import Any

from src.config.settings import settings
from src.domain.audit import AuditLogEntry, verify_chain
from src.repositories.interfaces import IAuditLogRepository, UnitOfWork


class AuditService:
    """Service for creating and verifying audit log entries.

    Every consent action is logged immutably. The audit log uses a
    SHA-256 hash chain for tamper evidence.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self._audit_secret = settings.jwt_secret  # Reuse JWT secret for HMAC

    def log(
        self,
        tenant_id: str,
        action: str,
        actor: str,
        payload: dict[str, Any],
    ) -> AuditLogEntry:
        """Create an audit log entry, chained to the previous entry."""
        repo: IAuditLogRepository = self._uow.audit_logs
        latest = repo.get_latest(tenant_id)
        prev_hash = latest.hash_value if latest else ""

        entry = AuditLogEntry.create(
            tenant_id=tenant_id,
            action=action,
            actor=actor,
            payload=payload,
            prev_hash=prev_hash,
            secret=self._audit_secret,
        )
        return repo.save(entry)

    def verify_tenant_chain(self, tenant_id: str) -> tuple[bool, str | None]:
        """Verify the entire audit chain for a tenant."""
        repo: IAuditLogRepository = self._uow.audit_logs
        entries = repo.list_by_tenant(tenant_id)
        return verify_chain(entries, secret=self._audit_secret)
