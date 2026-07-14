"""Tests for RightsService with mocked repositories."""

from unittest.mock import create_autospec

import pytest

from src.domain.exceptions import InvalidRightsRequestError
from src.domain.rights import (
    GrievanceStatus,
    RightsRequest,
    RightsRequestStatus,
    RightsRequestType,
)
from src.repositories.interfaces import (
    IGrievanceRepository,
    IRightsRequestRepository,
    UnitOfWork,
)
from src.services.audit_service import AuditService
from src.services.rights_service import RightsService


@pytest.fixture
def mock_uow():
    uow = create_autospec(UnitOfWork)
    uow.__enter__.return_value = uow
    uow.__exit__.return_value = None
    uow.rights_requests = create_autospec(IRightsRequestRepository)
    uow.grievances = create_autospec(IGrievanceRepository)
    from src.repositories.interfaces import IAuditLogRepository

    uow.audit_logs = create_autospec(IAuditLogRepository)
    uow.audit_logs.get_latest.return_value = None
    return uow


@pytest.fixture
def mock_audit_service(mock_uow):
    return AuditService(uow=mock_uow)


@pytest.fixture
def rights_service(mock_uow, mock_audit_service):
    return RightsService(uow=mock_uow, audit_service=mock_audit_service)


class TestRightsRequest:
    def test_submit_request(self, rights_service, mock_uow):
        result = rights_service.submit_rights_request(
            tenant_id="t1",
            principal_ref="user-123",
            request_type=RightsRequestType.ACCESS,
        )
        assert result.request_type == RightsRequestType.ACCESS
        assert result.status == RightsRequestStatus.SUBMITTED
        mock_uow.commit.assert_called_once()

    def test_submit_all_request_types(self, rights_service, mock_uow):
        for rtype in RightsRequestType:
            result = rights_service.submit_rights_request(
                tenant_id="t1",
                principal_ref="user-1",
                request_type=rtype,
            )
            assert result.request_type == rtype
            assert result.status == RightsRequestStatus.SUBMITTED

    def test_resolve_request(self, rights_service, mock_uow):
        mock_req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.ACCESS,
        )
        mock_uow.rights_requests.get_by_id.return_value = mock_req

        result = rights_service.resolve_request(
            request_id=mock_req.id,
            tenant_id="t1",
            notes="Data access granted",
        )
        assert result.status == RightsRequestStatus.RESOLVED
        mock_uow.commit.assert_called_once()

    def test_resolve_nonexistent_request_raises_error(self, rights_service, mock_uow):
        mock_uow.rights_requests.get_by_id.return_value = None

        with pytest.raises(InvalidRightsRequestError, match="not found"):
            rights_service.resolve_request(
                request_id="nonexistent",
                tenant_id="t1",
            )

    def test_get_pending(self, rights_service, mock_uow):
        mock_uow.rights_requests.list_pending.return_value = []
        result = rights_service.get_pending_requests("t1")
        assert result == []


class TestGrievance:
    def test_submit_grievance(self, rights_service, mock_uow):
        result = rights_service.submit_grievance(
            tenant_id="t1",
            principal_ref="user-123",
            subject="Data not deleted",
            description="I requested erasure but data still exists",
        )
        assert result.status == GrievanceStatus.OPEN
        mock_uow.commit.assert_called_once()

    def test_acknowledge_grievance(self, rights_service, mock_uow):
        from src.domain.rights import Grievance

        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Test",
            description="Test",
        )
        mock_uow.grievances.get_by_id.return_value = grievance

        result = rights_service.acknowledge_grievance(
            grievance_id=grievance.id,
            tenant_id="t1",
        )
        assert result.status == GrievanceStatus.ACKNOWLEDGED

    def test_resolve_grievance(self, rights_service, mock_uow):
        from src.domain.rights import Grievance

        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Test",
            description="Test",
        )
        mock_uow.grievances.get_by_id.return_value = grievance

        result = rights_service.resolve_grievance(
            grievance_id=grievance.id,
            tenant_id="t1",
        )
        assert result.status == GrievanceStatus.RESOLVED
