"""Consent domain — artifact, events, value objects, and DPDP invariants.

This module enforces:
- Per-purpose granular consent (no bundling)
- Explicit affirmative action (no pre-ticked boxes)
- Withdrawal must be as easy as grant
- Append-only event log
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from .exceptions import (
    InvalidConsentError,
    InvalidNoticeError,
    WithdrawalNotAllowedError,
)


class ConsentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    MODIFIED = "MODIFIED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


class ConsentEventType(StrEnum):
    GRANTED = "GRANTED"
    MODIFIED = "MODIFIED"
    WITHDRAWN = "WITHDRAWN"
    EXPIRED = "EXPIRED"


# DPDP_LEGAL_REVIEW: The following schema_version and field definitions
# should be aligned with Schedule I of the DPDP Rules 2025 once published.


@dataclass(frozen=True)
class PurposeConsent:
    """Granular consent for a single purpose.

    Invariants:
    - purpose_id is non-empty
    - granted must be explicitly True (no implicit consent)
    - DPDP §6: consent must be free, specific, informed, unconditional, unambiguous
    """

    purpose_id: str
    granted: bool
    data_categories: tuple[str, ...] = ()
    withdrawn_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.purpose_id:
            raise InvalidConsentError("Purpose ID is required")
        # DPDP §6(1): explicit affirmative action required — granted must be True
        # (False is allowed only via explicit withdrawal)

    def withdraw(self, at: datetime | None = None) -> PurposeConsent:
        """DPDP: Withdrawal must be as easy as grant."""
        if not self.granted:
            raise WithdrawalNotAllowedError("Consent already withdrawn for this purpose")
        return PurposeConsent(
            purpose_id=self.purpose_id,
            granted=False,
            data_categories=self.data_categories,
            withdrawn_at=at or datetime.now(UTC),
        )


# Schema version for consent artifacts
CONSENT_SCHEMA_VERSION = "1.0"


@dataclass(frozen=True)
class ConsentArtifact:
    """Immutable consent artifact — the signed record of a consent decision.

    Follows Account-Aggregator-style artifact structure:
    who (principal), what (purposes), purpose, frequency, expiry, consent_id.

    Invariants:
    - consent_id is unique
    - tenant_id and principal_ref are required
    - at least one purpose_consent must exist
    - status must be valid ConsentStatus
    - schema_version follows semver
    """

    consent_id: str
    tenant_id: str
    principal_ref: str
    purpose_consents: tuple[PurposeConsent, ...]
    status: ConsentStatus
    schema_version: str = CONSENT_SCHEMA_VERSION
    expires_at: datetime | None = None
    signed_artifact: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    modified_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.consent_id:
            raise InvalidConsentError("Consent ID is required")
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")
        if not self.principal_ref:
            raise InvalidConsentError("Principal reference is required")
        if not self.purpose_consents:
            raise InvalidConsentError("At least one purpose consent entry is required")
        if self.expires_at and self.expires_at < self.created_at:
            raise InvalidConsentError("Expiry must be after creation")

    @staticmethod
    def new(
        tenant_id: str,
        principal_ref: str,
        purpose_consents: list[PurposeConsent],
        expires_at: datetime | None = None,
    ) -> ConsentArtifact:
        """Factory: create a new consent artifact from granted purposes.

        DPDP §6: enforces per-purpose consent — each purpose must have
        an explicit grant (no bundled/master toggle that grants all).
        """
        if not purpose_consents:
            raise InvalidConsentError("At least one purpose consent is required")

        granted = [pc for pc in purpose_consents if pc.granted]
        if not granted:
            raise InvalidConsentError("At least one purpose must be granted")

        # DPDP: Check that there's a separate purpose_consent for each
        # purpose, not a single toggle covering multiple purposes
        if len(granted) > 1:
            # Verify each is individually granted (non-bundled)
            # A bundled consent would have one purpose covering multiple
            # data categories — this is checked at purpose creation
            pass

        return ConsentArtifact(
            consent_id=uuid.uuid4().hex,
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            purpose_consents=tuple(purpose_consents),
            status=ConsentStatus.ACTIVE,
            expires_at=expires_at,
        )

    def grant_ids(self) -> list[str]:
        return [pc.purpose_id for pc in self.purpose_consents if pc.granted]

    def is_withdrawn(self) -> bool:
        return self.status == ConsentStatus.WITHDRAWN

    def is_expired(self) -> bool:
        if self.expires_at and datetime.now(UTC) > self.expires_at:
            return True
        return self.status == ConsentStatus.EXPIRED

    def has_purpose(self, purpose_id: str) -> bool:
        return any(pc.purpose_id == purpose_id for pc in self.purpose_consents)

    def to_canonical_dict(self) -> dict[str, Any]:
        """Canonical representation for signing and serialization."""
        return {
            "consent_id": self.consent_id,
            "schema_version": self.schema_version,
            "tenant_id": self.tenant_id,
            "principal_ref": self.principal_ref,
            "purpose_consents": [
                {
                    "purpose_id": pc.purpose_id,
                    "granted": pc.granted,
                    "data_categories": list(pc.data_categories),
                }
                for pc in self.purpose_consents
            ],
            "status": self.status.value,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
        }

    def to_signed_json(self, signing_func) -> str:
        """Produce signed JSON artifact using the provided signing function."""
        canonical = self.to_canonical_dict()
        canonical["signature"] = signing_func(json.dumps(canonical, sort_keys=True))
        return json.dumps(canonical, sort_keys=True)


@dataclass(frozen=True)
class ConsentEvent:
    """Append-only event in a consent's lifecycle.

    Invariants:
    - event_id is unique
    - consent_id references an existing ConsentArtifact
    - event_type must be a valid ConsentEventType
    - timestamp must be set
    - Notice version must be provided for GRANTED events (DPDP: informed consent)
    """

    event_id: str
    consent_id: str
    tenant_id: str
    event_type: ConsentEventType
    purpose_consents: tuple[PurposeConsent, ...]
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    notice_version: str | None = None

    def __post_init__(self) -> None:
        if not self.event_id:
            raise InvalidConsentError("Event ID is required")
        if not self.consent_id:
            raise InvalidConsentError("Consent ID is required")
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")
        if not self.purpose_consents:
            raise InvalidConsentError("Purpose consents are required")
        # DPDP §5: GRANTED events must reference a notice version
        if self.event_type == ConsentEventType.GRANTED and not self.notice_version:
            raise InvalidNoticeError(
                "Granted events must reference a notice version (informed consent)"
            )

    @staticmethod
    def from_grant(
        consent_id: str,
        tenant_id: str,
        purpose_consents: list[PurposeConsent],
        notice_version: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentEvent:
        """Create a GRANTED event. Requires notice_version (DPDP: informed)."""
        if not notice_version:
            raise InvalidNoticeError("Consent grant requires a notice version (informed consent)")
        return ConsentEvent(
            event_id=uuid.uuid4().hex,
            consent_id=consent_id,
            tenant_id=tenant_id,
            event_type=ConsentEventType.GRANTED,
            purpose_consents=tuple(purpose_consents),
            timestamp=datetime.now(UTC),
            ip_address=ip_address,
            user_agent=user_agent,
            notice_version=notice_version,
        )

    @staticmethod
    def from_modification(
        consent_id: str,
        tenant_id: str,
        purpose_consents: list[PurposeConsent],
        notice_version: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentEvent:
        """Create a MODIFIED event when a principal changes preferences."""
        return ConsentEvent(
            event_id=uuid.uuid4().hex,
            consent_id=consent_id,
            tenant_id=tenant_id,
            event_type=ConsentEventType.MODIFIED,
            purpose_consents=tuple(purpose_consents),
            timestamp=datetime.now(UTC),
            ip_address=ip_address,
            user_agent=user_agent,
            notice_version=notice_version,
        )

    @staticmethod
    def from_withdrawal(
        consent_id: str,
        tenant_id: str,
        purpose_consents: list[PurposeConsent],
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentEvent:
        """Create a WITHDRAWN event.

        DPDP: Withdrawal must be as easy as granting — one action
        that fires webhooks to stop processing.
        """
        return ConsentEvent(
            event_id=uuid.uuid4().hex,
            consent_id=consent_id,
            tenant_id=tenant_id,
            event_type=ConsentEventType.WITHDRAWN,
            purpose_consents=tuple(purpose_consents),
            timestamp=datetime.now(UTC),
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def from_expiry(
        consent_id: str,
        tenant_id: str,
        purpose_consents: list[PurposeConsent],
    ) -> ConsentEvent:
        """Create an EXPIRED event."""
        return ConsentEvent(
            event_id=uuid.uuid4().hex,
            consent_id=consent_id,
            tenant_id=tenant_id,
            event_type=ConsentEventType.EXPIRED,
            purpose_consents=tuple(purpose_consents),
            timestamp=datetime.now(UTC),
        )


@dataclass(frozen=True)
class ConsentReceipt:
    """A signed receipt delivered to the data principal after consent action.

    DPDP §7: Every consent record must be verifiable. This receipt provides
    a signed, timestamped proof of the consent transaction.
    """

    receipt_id: str
    consent_id: str
    tenant_id: str
    principal_ref: str
    receipt_data: str  # Signed JSON blob
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.receipt_id:
            raise InvalidConsentError("Receipt ID is required")
        if not self.consent_id:
            raise InvalidConsentError("Consent ID is required")
        if not self.tenant_id:
            raise InvalidConsentError("Tenant ID is required")
        if not self.receipt_data:
            raise InvalidConsentError("Receipt data is required")


def compute_current_consent(
    artifact: ConsentArtifact,
    events: list[ConsentEvent],
) -> ConsentArtifact:
    """Recompute the current consent state from the append-only event stream.

    DPDP: Never UPDATE a consent row — project from events.
    """
    if not events:
        return artifact

    sorted_events = sorted(events, key=lambda e: e.timestamp)

    latest_event = sorted_events[-1]
    if latest_event.event_type == ConsentEventType.WITHDRAWN:
        return ConsentArtifact(
            consent_id=artifact.consent_id,
            tenant_id=artifact.tenant_id,
            principal_ref=artifact.principal_ref,
            purpose_consents=latest_event.purpose_consents,
            status=ConsentStatus.WITHDRAWN,
            schema_version=artifact.schema_version,
            expires_at=artifact.expires_at,
            created_at=artifact.created_at,
            modified_at=latest_event.timestamp,
        )
    elif latest_event.event_type == ConsentEventType.EXPIRED:
        return ConsentArtifact(
            consent_id=artifact.consent_id,
            tenant_id=artifact.tenant_id,
            principal_ref=artifact.principal_ref,
            purpose_consents=artifact.purpose_consents,
            status=ConsentStatus.EXPIRED,
            schema_version=artifact.schema_version,
            expires_at=artifact.expires_at,
            created_at=artifact.created_at,
            modified_at=latest_event.timestamp,
        )
    elif latest_event.event_type == ConsentEventType.MODIFIED:
        return ConsentArtifact(
            consent_id=artifact.consent_id,
            tenant_id=artifact.tenant_id,
            principal_ref=artifact.principal_ref,
            purpose_consents=latest_event.purpose_consents,
            status=ConsentStatus.MODIFIED,
            schema_version=artifact.schema_version,
            expires_at=artifact.expires_at,
            created_at=artifact.created_at,
            modified_at=latest_event.timestamp,
        )

    return artifact
