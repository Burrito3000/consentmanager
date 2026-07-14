"""Tests for the tamper-evident audit hash chain."""

import pytest

from src.domain.audit import (
    AuditLogEntry,
    canonical_json,
    compute_hash,
    verify_chain,
)
from src.domain.exceptions import InvalidAuditChainError


class TestAuditLogEntry:
    def test_create_entry_with_empty_prev_hash(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1", "purpose": "marketing"},
        )
        assert entry.prev_hash == ""
        assert entry.hash_value is not None
        assert len(entry.hash_value) == 64  # SHA-256 hex
        assert entry.retention_until is not None

    def test_create_entry_with_prev_hash(self) -> None:
        first = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )
        second = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.modified",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
            prev_hash=first.hash_value,
        )
        assert second.prev_hash == first.hash_value
        assert second.hash_value != first.hash_value

    def test_verify_valid_entry(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )
        assert entry.verify() is True

    def test_verify_tampered_payload(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )
        # Tamper with the payload by creating a modified version
        tampered = AuditLogEntry(
            entry_id=entry.entry_id,
            tenant_id=entry.tenant_id,
            prev_hash=entry.prev_hash,
            hash_value=entry.hash_value,
            payload={"consent_id": "c1", "tampered": True},
            action=entry.action,
            actor=entry.actor,
            timestamp=entry.timestamp,
        )
        assert tampered.verify() is False

    def test_create_with_hmac_secret(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
            secret="my-secret",
        )
        assert entry.verify(secret="my-secret") is True
        assert entry.verify(secret="wrong-secret") is False

    def test_create_entry_missing_required_fields_raises_error(self) -> None:
        with pytest.raises(InvalidAuditChainError, match="Action"):
            AuditLogEntry(
                entry_id="e1",
                tenant_id="t1",
                prev_hash="",
                hash_value="abc",
                payload={},
                action="",
                actor="test",
                timestamp=__import__("datetime").datetime.now(__import__("datetime").timezone.utc),
            )


class TestVerifyChain:
    def test_empty_chain_is_valid(self) -> None:
        valid, bad_id = verify_chain([])
        assert valid is True
        assert bad_id is None

    def test_single_entry_chain_is_valid(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )
        valid, bad_id = verify_chain([entry])
        assert valid is True

    def test_valid_multi_entry_chain(self) -> None:
        entries = []
        prev_hash = ""
        for i in range(3):
            entry = AuditLogEntry.create(
                tenant_id="t1",
                action=f"action.{i}",
                actor="system",
                payload={"index": i},
                prev_hash=prev_hash,
            )
            entries.append(entry)
            prev_hash = entry.hash_value

        valid, bad_id = verify_chain(entries)
        assert valid is True

    def test_broken_chain_detected(self) -> None:
        e1 = AuditLogEntry.create(
            tenant_id="t1",
            action="action.0",
            actor="system",
            payload={"index": 0},
        )
        # Second entry with wrong prev_hash
        e2 = AuditLogEntry.create(
            tenant_id="t1",
            action="action.1",
            actor="system",
            payload={"index": 1},
            prev_hash="wrong-hash",
        )
        valid, bad_id = verify_chain([e1, e2])
        assert valid is False
        assert bad_id == e2.entry_id

    def test_first_entry_with_non_empty_prev_hash_fails(self) -> None:
        entry = AuditLogEntry.create(
            tenant_id="t1",
            action="action.0",
            actor="system",
            payload={"index": 0},
            prev_hash="non-empty",
        )
        valid, bad_id = verify_chain([entry])
        assert valid is False


class TestComputeHash:
    def test_deterministic_hash(self) -> None:
        payload = {"key": "value", "number": 42}
        h1 = compute_hash("", payload)
        h2 = compute_hash("", payload)
        assert h1 == h2

    def test_different_payloads_different_hashes(self) -> None:
        h1 = compute_hash("", {"a": 1})
        h2 = compute_hash("", {"a": 2})
        assert h1 != h2


class TestCanonicalJSON:
    def test_sorted_keys(self) -> None:
        result = canonical_json({"z": 1, "a": 2})
        assert result == '{"a":2,"z":1}'
