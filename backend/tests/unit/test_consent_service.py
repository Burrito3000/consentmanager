"""Tests for ConsentService with mocked repositories."""

from unittest.mock import MagicMock, create_autospec

import pytest

from src.domain.consent import (
    ConsentStatus,
    PurposeConsent,
)
from src.domain.exceptions import (
    ConsentExpiredError,
    ConsentNotFoundError,
    InvalidConsentError,
)
from src.repositories.interfaces import (
    IAuditLogRepository,
    IConsentEventRepository,
    IConsentReceiptRepository,
    IConsentRepository,
    IDataPrincipalRepository,
    IPurposeRepository,
    UnitOfWork,
)
from src.services.audit_service import AuditService
from src.services.consent_service import ConsentService


@pytest.fixture
def mock_uow():
    uow = create_autospec(UnitOfWork)
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.consents = create_autospec(IConsentRepository)
    uow.consent_events = create_autospec(IConsentEventRepository)
    uow.consent_receipts = create_autospec(IConsentReceiptRepository)
    uow.principals = create_autospec(IDataPrincipalRepository)
    uow.purposes = create_autospec(IPurposeRepository)
    uow.audit_logs = create_autospec(IAuditLogRepository)
    uow.audit_logs.get_latest.return_value = None
    return uow


@pytest.fixture
def mock_audit_service(mock_uow):
    return AuditService(uow=mock_uow)


@pytest.fixture
def consent_service(mock_uow, mock_audit_service):
    return ConsentService(uow=mock_uow, audit_service=mock_audit_service)


class TestGrantConsent:
    def test_grant_single_purpose(self, consent_service, mock_uow):
        mock_uow.purposes.get_by_id.return_value = MagicMock(
            id="p1", is_active=True, tenant_id="t1"
        )
        mock_uow.consents.save.return_value = MagicMock()
        mock_uow.consent_events.save.return_value = MagicMock()
        mock_uow.consent_receipts.save.return_value = MagicMock()

        result = consent_service.grant_consent(
            tenant_id="t1",
            principal_ref="user-123",
            purpose_grants=[
                {"purpose_id": "p1", "granted": True, "data_categories": ["email"]},
            ],
            notice_version="v1.0-en",
        )

        assert result["status"] == ConsentStatus.ACTIVE.value
        assert result["consent_id"] is not None
        mock_uow.commit.assert_called_once()

    def test_grant_without_explicit_grant_raises_error(self, consent_service, mock_uow):
        mock_uow.purposes.get_by_id.return_value = MagicMock(
            id="p1", is_active=True, tenant_id="t1"
        )

        with pytest.raises(InvalidConsentError, match="explicit grant"):
            consent_service.grant_consent(
                tenant_id="t1",
                principal_ref="user-123",
                purpose_grants=[
                    {"purpose_id": "p1", "granted": False},
                ],
                notice_version="v1.0-en",
            )

    def test_grant_inactive_purpose_raises_error(self, consent_service, mock_uow):
        mock_uow.purposes.get_by_id.return_value = MagicMock(id="p1", is_active=False)

        with pytest.raises(InvalidConsentError, match="not found or inactive"):
            consent_service.grant_consent(
                tenant_id="t1",
                principal_ref="user-123",
                purpose_grants=[
                    {"purpose_id": "p1", "granted": True},
                ],
                notice_version="v1.0-en",
            )

    def test_grant_multiple_purposes_per_purpose(self, consent_service, mock_uow):
        """DPDP: Multiple purposes each need individual grant."""
        mock_uow.purposes.get_by_id.side_effect = [
            MagicMock(id="p1", is_active=True, tenant_id="t1"),
            MagicMock(id="p2", is_active=True, tenant_id="t1"),
        ]

        result = consent_service.grant_consent(
            tenant_id="t1",
            principal_ref="user-123",
            purpose_grants=[
                {"purpose_id": "p1", "granted": True, "data_categories": ["email"]},
                {"purpose_id": "p2", "granted": True, "data_categories": ["name"]},
            ],
            notice_version="v1.0-en",
        )

        assert result["status"] == ConsentStatus.ACTIVE.value


class TestModifyConsent:
    def test_modify_granted_consent(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
            status=ConsentStatus.ACTIVE,
            is_withdrawn=lambda: False,
            is_expired=lambda: False,
            purpose_consents=(),
        )
        mock_uow.consent_events.list_by_consent.return_value = []
        mock_uow.consent_events.save.return_value = MagicMock()

        result = consent_service.modify_consent(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
            purpose_grants=[
                {"purpose_id": "p1", "granted": True, "data_categories": ["email", "name"]},
            ],
        )

        assert result["consent_id"] == "c1"
        mock_uow.commit.assert_called_once()

    def test_modify_withdrawn_consent_raises_error(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
            status=ConsentStatus.WITHDRAWN,
            is_withdrawn=lambda: True,
            is_expired=lambda: False,
            purpose_consents=(),
        )

        with pytest.raises(InvalidConsentError, match="withdrawn"):
            consent_service.modify_consent(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="user-123",
                purpose_grants=[{"purpose_id": "p1", "granted": True}],
            )

    def test_modify_expired_consent_raises_error(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
            status=ConsentStatus.EXPIRED,
            is_withdrawn=lambda: False,
            is_expired=lambda: True,
            purpose_consents=(),
        )

        with pytest.raises(ConsentExpiredError):
            consent_service.modify_consent(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="user-123",
                purpose_grants=[{"purpose_id": "p1", "granted": True}],
            )

    def test_modify_wrong_principal_raises_error(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="other-user",
            is_withdrawn=lambda: False,
            is_expired=lambda: False,
        )

        with pytest.raises(InvalidConsentError, match="mismatch"):
            consent_service.modify_consent(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="user-123",
                purpose_grants=[{"purpose_id": "p1", "granted": True}],
            )


class TestWithdrawConsent:
    def test_withdraw_consent(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
            status=ConsentStatus.ACTIVE,
            is_withdrawn=lambda: False,
            is_expired=lambda: False,
            purpose_consents=(
                PurposeConsent(purpose_id="p1", granted=True, data_categories=("email",)),
            ),
        )
        mock_uow.consent_events.list_by_consent.return_value = []

        result = consent_service.withdraw_consent(
            consent_id="c1",
            tenant_id="t1",
            principal_ref="user-123",
        )

        assert result["status"] == ConsentStatus.WITHDRAWN.value
        mock_uow.commit.assert_called_once()

    def test_withdraw_already_withdrawn_raises_error(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            is_withdrawn=lambda: True,
        )

        with pytest.raises(InvalidConsentError, match="already withdrawn"):
            consent_service.withdraw_consent(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="user-123",
            )

    def test_withdraw_wrong_tenant_raises_error(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="other-tenant",
        )

        with pytest.raises(ConsentNotFoundError):
            consent_service.withdraw_consent(
                consent_id="c1",
                tenant_id="t1",
                principal_ref="user-123",
            )


class TestGetConsent:
    def test_get_existing_consent(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="t1",
            status=ConsentStatus.ACTIVE,
        )
        mock_uow.consent_events.list_by_consent.return_value = []

        result = consent_service.get_consent(
            consent_id="c1",
            tenant_id="t1",
        )

        assert result is not None
        assert result["current_status"] == ConsentStatus.ACTIVE.value

    def test_get_wrong_tenant_returns_none(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = MagicMock(
            consent_id="c1",
            tenant_id="other-tenant",
        )

        result = consent_service.get_consent(
            consent_id="c1",
            tenant_id="t1",
        )

        assert result is None

    def test_get_nonexistent_consent_returns_none(self, consent_service, mock_uow):
        mock_uow.consents.get_by_id.return_value = None

        result = consent_service.get_consent(
            consent_id="nonexistent",
            tenant_id="t1",
        )

        assert result is None
