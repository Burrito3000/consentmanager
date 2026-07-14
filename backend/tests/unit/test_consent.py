"""Tests for consent domain entities — artifact, events, invariants.

DPDP compliance tests:
- Per-purpose granular consent (no bundling)
- Explicit affirmative action
- Withdrawal as easy as grant
- Append-only event log
"""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.consent import (
    CONSENT_SCHEMA_VERSION,
    ConsentArtifact,
    ConsentEvent,
    ConsentEventType,
    ConsentStatus,
    PurposeConsent,
    compute_current_consent,
)
from src.domain.exceptions import (
    InvalidConsentError,
    InvalidNoticeError,
    WithdrawalNotAllowedError,
)


class TestPurposeConsent:
    def test_create_granted_consent(self) -> None:
        pc = PurposeConsent(purpose_id="p1", granted=True)
        assert pc.granted is True
        assert pc.withdrawn_at is None

    def test_create_without_purpose_id_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="Purpose ID"):
            PurposeConsent(purpose_id="", granted=True)

    def test_withdraw_purpose_consent(self) -> None:
        pc = PurposeConsent(purpose_id="p1", granted=True)
        withdrawn = pc.withdraw()
        assert withdrawn.granted is False
        assert withdrawn.withdrawn_at is not None

    def test_withdraw_already_withdrawn_raises_error(self) -> None:
        pc = PurposeConsent(purpose_id="p1", granted=False)
        with pytest.raises(WithdrawalNotAllowedError):
            pc.withdraw()


class TestConsentArtifact:
    def test_create_new_consent_artifact(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
            PurposeConsent(purpose_id="p2", granted=True, data_categories=("name",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="tenant-1",
            principal_ref="user-123",
            purpose_consents=purposes,
        )
        assert artifact.status == ConsentStatus.ACTIVE
        assert artifact.tenant_id == "tenant-1"
        assert artifact.principal_ref == "user-123"
        assert len(artifact.purpose_consents) == 2
        assert artifact.schema_version == CONSENT_SCHEMA_VERSION

    def test_create_consent_with_no_granted_purposes_raises_error(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=False),
        ]
        with pytest.raises(InvalidConsentError, match="granted"):
            ConsentArtifact.new(
                tenant_id="tenant-1",
                principal_ref="user-123",
                purpose_consents=purposes,
            )

    def test_create_consent_with_no_purposes_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="purpose consent is required"):
            ConsentArtifact.new(
                tenant_id="tenant-1",
                principal_ref="user-123",
                purpose_consents=[],
            )

    def test_consent_expiry_check(self) -> None:
        now = datetime.now(UTC)
        past = now - timedelta(days=1)
        created = now - timedelta(days=30)
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=tuple(purposes),
            status=ConsentStatus.ACTIVE,
            expires_at=past,
            created_at=created,
        )
        assert artifact.is_expired() is True

    def test_consent_not_expired(self) -> None:
        future = datetime.now(UTC) + timedelta(days=30)
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=tuple(purposes),
            status=ConsentStatus.ACTIVE,
            expires_at=future,
        )
        assert artifact.is_expired() is False

    def test_is_withdrawn(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=False),
        ]
        artifact = ConsentArtifact(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=tuple(purposes),
            status=ConsentStatus.WITHDRAWN,
        )
        assert artifact.is_withdrawn() is True

    def test_to_canonical_dict(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        canonical = artifact.to_canonical_dict()
        assert canonical["consent_id"] == artifact.consent_id
        assert canonical["schema_version"] == CONSENT_SCHEMA_VERSION
        assert canonical["status"] == "ACTIVE"
        assert len(canonical["purpose_consents"]) == 1

    def test_consent_with_expiry_before_creation_raises_error(self) -> None:
        now = datetime.now(UTC)
        past = now - timedelta(days=1)
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True),
        ]
        with pytest.raises(InvalidConsentError, match="Expiry"):
            ConsentArtifact(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="u1",
                purpose_consents=tuple(purposes),
                status=ConsentStatus.ACTIVE,
                expires_at=past,
                created_at=now,
                modified_at=now,
            )


class TestConsentEvent:
    def test_create_granted_event_requires_notice_version(self) -> None:
        with pytest.raises(InvalidNoticeError, match="notice version"):
            ConsentEvent.from_grant(
                consent_id="c1",
                tenant_id="t1",
                purpose_consents=[PurposeConsent(purpose_id="p1", granted=True)],
                notice_version="",
            )

    def test_create_granted_event(self) -> None:
        event = ConsentEvent.from_grant(
            consent_id="c1",
            tenant_id="t1",
            purpose_consents=[PurposeConsent(purpose_id="p1", granted=True)],
            notice_version="v1.0-en",
            ip_address="192.168.1.1",
            user_agent="TestAgent/1.0",
        )
        assert event.event_type == ConsentEventType.GRANTED
        assert event.notice_version == "v1.0-en"
        assert event.ip_address == "192.168.1.1"

    def test_create_withdrawal_event(self) -> None:
        event = ConsentEvent.from_withdrawal(
            consent_id="c1",
            tenant_id="t1",
            purpose_consents=[PurposeConsent(purpose_id="p1", granted=False)],
        )
        assert event.event_type == ConsentEventType.WITHDRAWN

    def test_create_modification_event(self) -> None:
        event = ConsentEvent.from_modification(
            consent_id="c1",
            tenant_id="t1",
            purpose_consents=[PurposeConsent(purpose_id="p1", granted=True)],
            notice_version="v1.1-en",
        )
        assert event.event_type == ConsentEventType.MODIFIED

    def test_create_expiry_event(self) -> None:
        event = ConsentEvent.from_expiry(
            consent_id="c1",
            tenant_id="t1",
            purpose_consents=[PurposeConsent(purpose_id="p1", granted=False)],
        )
        assert event.event_type == ConsentEventType.EXPIRED


class TestComputeCurrentConsent:
    def test_no_events_returns_artifact_unchanged(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        result = compute_current_consent(artifact, [])
        assert result.status == ConsentStatus.ACTIVE

    def test_withdrawal_event_sets_withdrawn_status(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        withdraw_event = ConsentEvent.from_withdrawal(
            consent_id=artifact.consent_id,
            tenant_id="t1",
            purpose_consents=[
                PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",))
            ],
        )
        result = compute_current_consent(artifact, [withdraw_event])
        assert result.status == ConsentStatus.WITHDRAWN

    def test_expiry_event_sets_expired_status(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        expiry_event = ConsentEvent.from_expiry(
            consent_id=artifact.consent_id,
            tenant_id="t1",
            purpose_consents=[PurposeConsent(purpose_id="p1", granted=False)],
        )
        result = compute_current_consent(artifact, [expiry_event])
        assert result.status == ConsentStatus.EXPIRED

    def test_modification_event_sets_modified_status(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        modify_event = ConsentEvent.from_modification(
            consent_id=artifact.consent_id,
            tenant_id="t1",
            purpose_consents=[
                PurposeConsent(purpose_id="p1", granted=True, data_categories=("email", "name"))
            ],
            notice_version="v1.1",
        )
        result = compute_current_consent(artifact, [modify_event])
        assert result.status == ConsentStatus.MODIFIED

    def test_multiple_events_latest_wins(self) -> None:
        purposes = [
            PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
        ]
        artifact = ConsentArtifact.new(
            tenant_id="t1",
            principal_ref="u1",
            purpose_consents=purposes,
        )
        events = [
            ConsentEvent.from_modification(
                consent_id=artifact.consent_id,
                tenant_id="t1",
                purpose_consents=[
                    PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",))
                ],
            ),
            ConsentEvent.from_withdrawal(
                consent_id=artifact.consent_id,
                tenant_id="t1",
                purpose_consents=[
                    PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",))
                ],
            ),
        ]
        result = compute_current_consent(artifact, events)
        assert result.status == ConsentStatus.WITHDRAWN
