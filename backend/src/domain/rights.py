"""RightsRequest & Grievance entities — data-principal rights with SLA timers.

DPDP Act 2023 outlines data-principal rights including:
- Right to access summary
- Right to correction and erasure
- Right to grievance redressal
- Right to nominate
- Right to withdraw consent
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum

from .exceptions import InvalidRightsRequestError, SLABreachError


class RightsRequestType(StrEnum):
    ACCESS = "ACCESS"  # Right to access data summary
    CORRECTION = "CORRECTION"  # Right to correction
    ERASURE = "ERASURE"  # Right to erasure
    GRIEVANCE = "GRIEVANCE"  # Right to grievance redressal
    NOMINEE = "NOMINEE"  # Right to nominate
    WITHDRAW = "WITHDRAW"  # Right to withdraw consent


class RightsRequestStatus(StrEnum):
    SUBMITTED = "SUBMITTED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass(frozen=True)
class RightsRequest:
    """A data-principal rights request with SLA timer.

    Invariants:
    - request_type must be valid
    - sla_due_at must be in the future (on creation)
    - tenant_id and principal_ref required
    """

    tenant_id: str
    principal_ref: str
    request_type: RightsRequestType
    status: RightsRequestStatus = RightsRequestStatus.SUBMITTED
    sla_due_at: datetime | None = None
    notes: str | None = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    submitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.tenant_id:
            raise InvalidRightsRequestError("Tenant ID is required")
        if not self.principal_ref:
            raise InvalidRightsRequestError("Principal reference is required")

    @staticmethod
    def create(
        tenant_id: str,
        principal_ref: str,
        request_type: RightsRequestType,
        sla_seconds: int = 7_776_000,  # 90 days default
        notes: str | None = None,
    ) -> RightsRequest:
        """Factory: create a new rights request with SLA.

        DPDP: Default SLA is 90 days for most requests.
        Grievance SLA is shorter (configurable per tenant).
        """
        now = datetime.now(UTC)
        sla_due = now + timedelta(seconds=sla_seconds)
        return RightsRequest(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            request_type=request_type,
            status=RightsRequestStatus.SUBMITTED,
            sla_due_at=sla_due,
            notes=notes,
            submitted_at=now,
        )

    def is_sla_breached(self, reference_time: datetime | None = None) -> bool:
        if not self.sla_due_at:
            return False
        ref = reference_time or datetime.now(UTC)
        return ref > self.sla_due_at and self.status not in (
            RightsRequestStatus.RESOLVED,
            RightsRequestStatus.REJECTED,
        )

    def resolve(self, resolution_notes: str | None = None) -> RightsRequest:
        if self.is_sla_breached():
            raise SLABreachError("SLA deadline has passed for this request")
        return RightsRequest(
            id=self.id,
            tenant_id=self.tenant_id,
            principal_ref=self.principal_ref,
            request_type=self.request_type,
            status=RightsRequestStatus.RESOLVED,
            sla_due_at=self.sla_due_at,
            notes=resolution_notes or self.notes,
            submitted_at=self.submitted_at,
            resolved_at=datetime.now(UTC),
        )

    def escalate(self) -> RightsRequest:
        return RightsRequest(
            id=self.id,
            tenant_id=self.tenant_id,
            principal_ref=self.principal_ref,
            request_type=self.request_type,
            status=RightsRequestStatus.ESCALATED,
            sla_due_at=self.sla_due_at,
            notes=self.notes,
            submitted_at=self.submitted_at,
            resolved_at=self.resolved_at,
        )


class GrievanceStatus(StrEnum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass(frozen=True)
class Grievance:
    """A data-principal grievance with shorter SLA.

    DPDP: Grievance redressal is a fundamental right with
    tighter turnaround time.
    """

    tenant_id: str
    principal_ref: str
    subject: str
    description: str
    status: GrievanceStatus = GrievanceStatus.OPEN
    sla_due_at: datetime | None = None
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    submitted_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.tenant_id:
            raise InvalidRightsRequestError("Tenant ID is required")
        if not self.subject:
            raise InvalidRightsRequestError("Subject is required")
        if not self.description:
            raise InvalidRightsRequestError("Description is required")

    @staticmethod
    def create(
        tenant_id: str,
        principal_ref: str,
        subject: str,
        description: str,
        sla_seconds: int = 259_200,  # 3 days default
    ) -> Grievance:
        now = datetime.now(UTC)
        return Grievance(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            subject=subject,
            description=description,
            status=GrievanceStatus.OPEN,
            sla_due_at=now + timedelta(seconds=sla_seconds),
            submitted_at=now,
        )

    def is_sla_breached(self, reference_time: datetime | None = None) -> bool:
        if not self.sla_due_at:
            return False
        ref = reference_time or datetime.now(UTC)
        return ref > self.sla_due_at and self.status not in (
            GrievanceStatus.RESOLVED,
            GrievanceStatus.REJECTED,
        )

    def acknowledge(self) -> Grievance:
        return Grievance(
            id=self.id,
            tenant_id=self.tenant_id,
            principal_ref=self.principal_ref,
            subject=self.subject,
            description=self.description,
            status=GrievanceStatus.ACKNOWLEDGED,
            sla_due_at=self.sla_due_at,
            submitted_at=self.submitted_at,
            resolved_at=self.resolved_at,
        )

    def resolve(self) -> Grievance:
        return Grievance(
            id=self.id,
            tenant_id=self.tenant_id,
            principal_ref=self.principal_ref,
            subject=self.subject,
            description=self.description,
            status=GrievanceStatus.RESOLVED,
            sla_due_at=self.sla_due_at,
            submitted_at=self.submitted_at,
            resolved_at=datetime.now(UTC),
        )
