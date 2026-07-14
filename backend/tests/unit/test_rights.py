"""Tests for RightsRequest and Grievance domain entities."""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.exceptions import InvalidRightsRequestError, SLABreachError
from src.domain.rights import (
    Grievance,
    GrievanceStatus,
    RightsRequest,
    RightsRequestStatus,
    RightsRequestType,
)


class TestRightsRequest:
    def test_create_rights_request_with_sla(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-123",
            request_type=RightsRequestType.ACCESS,
            sla_seconds=7_776_000,
        )
        assert req.request_type == RightsRequestType.ACCESS
        assert req.status == RightsRequestStatus.SUBMITTED
        assert req.sla_due_at is not None
        assert req.id is not None

    def test_create_rights_request_missing_tenant_raises_error(self) -> None:
        with pytest.raises(InvalidRightsRequestError, match="Tenant"):
            RightsRequest(
                tenant_id="",
                principal_ref="user-1",
                request_type=RightsRequestType.ACCESS,
            )

    def test_sla_breach_detection(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.ACCESS,
            sla_seconds=1,  # 1 second SLA
        )
        past = req.submitted_at + timedelta(seconds=2)
        assert req.is_sla_breached(reference_time=past) is True

    def test_no_sla_breach_before_deadline(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.ACCESS,
            sla_seconds=7_776_000,
        )
        assert req.is_sla_breached() is False

    def test_resolve_request(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.CORRECTION,
        )
        resolved = req.resolve("Data corrected")
        assert resolved.status == RightsRequestStatus.RESOLVED
        assert resolved.resolved_at is not None

    def test_escalate_request(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.ERASURE,
        )
        escalated = req.escalate()
        assert escalated.status == RightsRequestStatus.ESCALATED

    def test_resolve_breached_sla_raises_error(self) -> None:
        req = RightsRequest.create(
            tenant_id="t1",
            principal_ref="user-1",
            request_type=RightsRequestType.ACCESS,
            sla_seconds=1,
        )
        # Manually set SLA in the past
        past = datetime.now(UTC) - timedelta(days=1)
        req = RightsRequest(
            id=req.id,
            tenant_id=req.tenant_id,
            principal_ref=req.principal_ref,
            request_type=req.request_type,
            status=req.status,
            sla_due_at=past,
            notes=req.notes,
            submitted_at=req.submitted_at,
        )
        with pytest.raises(SLABreachError):
            req.resolve()

    def test_all_request_types(self) -> None:
        for rtype in RightsRequestType:
            req = RightsRequest.create(
                tenant_id="t1",
                principal_ref="user-1",
                request_type=rtype,
            )
            assert req.request_type == rtype


class TestGrievance:
    def test_create_grievance_with_sla(self) -> None:
        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Data not deleted",
            description="I requested erasure but data still exists",
            sla_seconds=259_200,
        )
        assert grievance.subject == "Data not deleted"
        assert grievance.status == GrievanceStatus.OPEN
        assert grievance.sla_due_at is not None

    def test_acknowledge_grievance(self) -> None:
        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Test",
            description="Test description",
        )
        ack = grievance.acknowledge()
        assert ack.status == GrievanceStatus.ACKNOWLEDGED

    def test_resolve_grievance(self) -> None:
        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Test",
            description="Test description",
        )
        resolved = grievance.resolve()
        assert resolved.status == GrievanceStatus.RESOLVED
        assert resolved.resolved_at is not None

    def test_grievance_sla_breach(self) -> None:
        grievance = Grievance.create(
            tenant_id="t1",
            principal_ref="user-1",
            subject="Test",
            description="Test",
            sla_seconds=1,
        )
        past = grievance.submitted_at + timedelta(seconds=2)
        assert grievance.is_sla_breached(reference_time=past) is True

    def test_grievance_missing_subject_raises_error(self) -> None:
        with pytest.raises(InvalidRightsRequestError, match="Subject"):
            Grievance(
                tenant_id="t1",
                principal_ref="user-1",
                subject="",
                description="Test",
            )

    def test_grievance_missing_description_raises_error(self) -> None:
        with pytest.raises(InvalidRightsRequestError, match="Description"):
            Grievance(
                tenant_id="t1",
                principal_ref="user-1",
                subject="Test",
                description="",
            )
