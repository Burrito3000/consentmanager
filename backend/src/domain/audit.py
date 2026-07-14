"""Audit log — tamper-evident hash chain for DPDP compliance.

DPDP: All consent actions must be logged immutably. This module
provides a hash-chained audit log where each entry includes the
hash of the previous entry, creating a verifiable chain.

hash = SHA256(prev_hash + canonical_json(payload))
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from .exceptions import InvalidAuditChainError


def canonical_json(data: dict[str, Any]) -> str:
    """Deterministic JSON serialization with sorted keys."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def compute_hash(prev_hash: str, payload: dict[str, Any], secret: str = "") -> str:
    """Compute chain hash: SHA256(prev_hash + canonical_json(payload)).

    If a secret is provided, uses HMAC-SHA256 for additional tamper evidence.
    """
    canonical = canonical_json(payload)
    data = (prev_hash + canonical).encode("utf-8")
    if secret:
        return hmac.new(secret.encode("utf-8"), data, hashlib.sha256).hexdigest()
    return hashlib.sha256(data).hexdigest()


# DPDP_LEGAL_REVIEW: Retention period of 7 years for audit logs.
# This should be verified against the final DPDP Rules 2025.
AUDIT_RETENTION_YEARS = 7


@dataclass(frozen=True)
class AuditLogEntry:
    """A single entry in the tamper-evident audit log.

    Invariants:
    - entry_id is unique
    - prev_hash must match the previous entry's hash
    - hash is SHA256(prev_hash + canonical_json(payload))
    - action and actor are required
    """

    entry_id: str
    tenant_id: str
    prev_hash: str
    hash_value: str
    payload: dict[str, Any]
    action: str
    actor: str
    timestamp: datetime
    retention_until: datetime | None = None

    def __post_init__(self) -> None:
        if not self.entry_id:
            raise InvalidAuditChainError("Entry ID is required")
        if not self.tenant_id:
            raise InvalidAuditChainError("Tenant ID is required")
        if not self.action:
            raise InvalidAuditChainError("Action is required")
        if not self.actor:
            raise InvalidAuditChainError("Actor is required")

    @staticmethod
    def create(
        tenant_id: str,
        action: str,
        actor: str,
        payload: dict[str, Any],
        prev_hash: str = "",
        secret: str = "",
    ) -> AuditLogEntry:
        """Factory: create a new audit log entry with computed hash."""
        now = datetime.now(UTC)
        hash_value = compute_hash(prev_hash, payload, secret)
        retention_until = datetime(
            now.year + AUDIT_RETENTION_YEARS,
            now.month,
            now.day,
            tzinfo=UTC,
        )
        return AuditLogEntry(
            entry_id=uuid.uuid4().hex,
            tenant_id=tenant_id,
            prev_hash=prev_hash,
            hash_value=hash_value,
            payload=payload,
            timestamp=now,
            action=action,
            actor=actor,
            retention_until=retention_until,
        )

    def verify(self, secret: str = "") -> bool:
        """Verify that this entry's hash matches its content."""
        expected = compute_hash(self.prev_hash, self.payload, secret)
        return hmac.compare_digest(expected, self.hash_value)


def verify_chain(entries: list[AuditLogEntry], secret: str = "") -> tuple[bool, str | None]:
    """Verify an entire hash chain. Returns (is_valid, first_bad_entry_id).

    DPDP: Tamper-evident audit trail — if any entry has been modified,
    the chain will break.
    """
    if not entries:
        return True, None

    sorted_entries = sorted(entries, key=lambda e: e.timestamp)

    # First entry must have empty prev_hash
    if sorted_entries[0].prev_hash:
        return False, sorted_entries[0].entry_id

    for i, entry in enumerate(sorted_entries):
        if not entry.verify(secret):
            return False, entry.entry_id
        # Verify chain continuity
        if i > 0 and sorted_entries[i - 1].hash_value != entry.prev_hash:
            return False, entry.entry_id

    return True, None
