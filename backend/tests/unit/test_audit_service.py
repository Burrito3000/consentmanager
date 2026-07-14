"""Tests for AuditService with mocked repositories."""

from unittest.mock import MagicMock, create_autospec

import pytest

from src.repositories.interfaces import IAuditLogRepository, UnitOfWork
from src.services.audit_service import AuditService


@pytest.fixture
def mock_uow():
    uow = create_autospec(UnitOfWork)
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.audit_logs = create_autospec(IAuditLogRepository)
    uow.audit_logs.get_latest.return_value = None
    return uow


@pytest.fixture
def audit_service(mock_uow):
    return AuditService(uow=mock_uow)


class TestAuditService:
    def test_log_first_entry(self, audit_service, mock_uow):
        mock_uow.audit_logs.get_latest.return_value = None

        audit_service.log(
            tenant_id="t1",
            action="consent.granted",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )

        mock_uow.audit_logs.save.assert_called_once()
        saved_entry = mock_uow.audit_logs.save.call_args[0][0]
        assert saved_entry.action == "consent.granted"
        assert saved_entry.prev_hash == ""
        assert len(saved_entry.hash_value) == 64

    def test_log_chained_entry(self, audit_service, mock_uow):
        prev_mock = MagicMock()
        prev_mock.hash_value = "prev_hash_123"
        mock_uow.audit_logs.get_latest.return_value = prev_mock

        audit_service.log(
            tenant_id="t1",
            action="consent.modified",
            actor="principal:user-123",
            payload={"consent_id": "c1"},
        )

        mock_uow.audit_logs.save.assert_called_once()
        saved_entry = mock_uow.audit_logs.save.call_args[0][0]
        assert saved_entry.prev_hash == "prev_hash_123"
        assert saved_entry.hash_value != "prev_hash_123"

    def test_verify_chain(self, audit_service, mock_uow):
        mock_uow.audit_logs.list_by_tenant.return_value = []
        valid, bad_id = audit_service.verify_tenant_chain("t1")
        assert valid is True
        assert bad_id is None
