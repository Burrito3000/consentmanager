"""Rights & Grievance service — data-principal rights with SLA timers."""

from __future__ import annotations

from src.config.settings import settings
from src.domain.exceptions import InvalidRightsRequestError
from src.domain.rights import (
    Grievance,
    RightsRequest,
    RightsRequestType,
)
from src.repositories.interfaces import (
    IGrievanceRepository,
    IRightsRequestRepository,
    UnitOfWork,
)
from src.services.audit_service import AuditService


class RightsService:
    """Service for managing data-principal rights requests and grievances.

    DPDP: Every rights request has an SLA timer (default 90 days for most,
    3 days for grievances). SLA breaches are detected and reported.
    """

    def __init__(self, uow: UnitOfWork, audit_service: AuditService) -> None:
        self._uow = uow
        self._audit = audit_service

    def submit_rights_request(
        self,
        tenant_id: str,
        principal_ref: str,
        request_type: RightsRequestType,
        notes: str | None = None,
        sla_seconds: int | None = None,
    ) -> RightsRequest:
        """Submit a new data-principal rights request with SLA."""
        sla = sla_seconds or settings.sla_rights_request
        request = RightsRequest.create(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            request_type=request_type,
            sla_seconds=sla,
            notes=notes,
        )

        with self._uow:
            repo: IRightsRequestRepository = self._uow.rights_requests
            repo.save(request)

            self._audit.log(
                tenant_id=tenant_id,
                action="rights_request.submitted",
                actor=f"principal:{principal_ref}",
                payload={
                    "request_id": request.id,
                    "request_type": request_type.value,
                    "sla_due_at": request.sla_due_at.isoformat() if request.sla_due_at else None,
                },
            )
            self._uow.commit()

        return request

    def resolve_request(
        self,
        request_id: str,
        tenant_id: str,
        notes: str | None = None,
    ) -> RightsRequest:
        """Resolve a rights request."""
        with self._uow:
            repo: IRightsRequestRepository = self._uow.rights_requests
            request = repo.get_by_id(request_id)
            if not request or request.tenant_id != tenant_id:
                raise InvalidRightsRequestError("Request not found")

            resolved = request.resolve(notes)
            repo.save(resolved)

            self._audit.log(
                tenant_id=tenant_id,
                action="rights_request.resolved",
                actor="system",
                payload={"request_id": request_id, "notes": notes},
            )
            self._uow.commit()

        return resolved

    def get_pending_requests(self, tenant_id: str) -> list[RightsRequest]:
        with self._uow:
            repo: IRightsRequestRepository = self._uow.rights_requests
            return repo.list_pending(tenant_id)

    def list_requests(
        self, tenant_id: str, principal_ref: str | None = None
    ) -> list[RightsRequest]:
        with self._uow:
            repo: IRightsRequestRepository = self._uow.rights_requests
            if principal_ref:
                return repo.list_by_principal(tenant_id, principal_ref)
            return repo.list_by_tenant(tenant_id)

    def check_sla_breaches(self, tenant_id: str) -> list[RightsRequest]:
        """Find all requests that have breached their SLA."""
        breached: list[RightsRequest] = []
        with self._uow:
            repo: IRightsRequestRepository = self._uow.rights_requests
            for req in repo.list_pending(tenant_id):
                if req.is_sla_breached():
                    breached.append(req)
        return breached

    def submit_grievance(
        self,
        tenant_id: str,
        principal_ref: str,
        subject: str,
        description: str,
        sla_seconds: int | None = None,
    ) -> Grievance:
        """Submit a grievance with shorter SLA (default 3 days)."""
        sla = sla_seconds or settings.sla_grievance
        grievance = Grievance.create(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            subject=subject,
            description=description,
            sla_seconds=sla,
        )

        with self._uow:
            repo: IGrievanceRepository = self._uow.grievances
            repo.save(grievance)

            self._audit.log(
                tenant_id=tenant_id,
                action="grievance.submitted",
                actor=f"principal:{principal_ref}",
                payload={
                    "grievance_id": grievance.id,
                    "subject": subject,
                    "sla_due_at": (
                        grievance.sla_due_at.isoformat() if grievance.sla_due_at else None
                    ),
                },
            )
            self._uow.commit()

        return grievance

    def acknowledge_grievance(self, grievance_id: str, tenant_id: str) -> Grievance:
        with self._uow:
            repo: IGrievanceRepository = self._uow.grievances
            grievance = repo.get_by_id(grievance_id)
            if not grievance or grievance.tenant_id != tenant_id:
                raise InvalidRightsRequestError("Grievance not found")

            updated = grievance.acknowledge()
            repo.save(updated)

            self._audit.log(
                tenant_id=tenant_id,
                action="grievance.acknowledged",
                actor="system",
                payload={"grievance_id": grievance_id},
            )
            self._uow.commit()

        return updated

    def resolve_grievance(self, grievance_id: str, tenant_id: str) -> Grievance:
        with self._uow:
            repo: IGrievanceRepository = self._uow.grievances
            grievance = repo.get_by_id(grievance_id)
            if not grievance or grievance.tenant_id != tenant_id:
                raise InvalidRightsRequestError("Grievance not found")

            updated = grievance.resolve()
            repo.save(updated)

            self._audit.log(
                tenant_id=tenant_id,
                action="grievance.resolved",
                actor="system",
                payload={"grievance_id": grievance_id},
            )
            self._uow.commit()

        return updated

    def list_open_grievances(self, tenant_id: str) -> list[Grievance]:
        with self._uow:
            repo: IGrievanceRepository = self._uow.grievances
            return repo.list_open(tenant_id)
