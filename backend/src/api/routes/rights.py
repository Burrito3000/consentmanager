"""Rights & Grievance API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import get_principal_ref_from_token, get_tenant_id_from_token
from src.api.schemas import (
    GrievanceCreate,
    GrievanceResponse,
    RightsRequestCreate,
    RightsRequestResponse,
)
from src.domain.exceptions import DomainError
from src.domain.rights import RightsRequestType
from src.services.container import ServiceContainer
from src.services.rights_service import RightsService

router = APIRouter(prefix="/rights", tags=["Rights & Grievance"])


def get_rights_service() -> RightsService:
    container = ServiceContainer()
    return container.rights_service()


@router.post(
    "/requests",
    response_model=RightsRequestResponse,
    summary="Submit a data-principal rights request",
)
async def submit_request(
    body: RightsRequestCreate,
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: RightsService = Depends(get_rights_service),
) -> RightsRequestResponse:
    if body.principal_ref != principal_ref:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Principal mismatch")

    try:
        request = service.submit_rights_request(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            request_type=RightsRequestType(body.request_type),
            notes=body.notes,
        )
        return RightsRequestResponse(
            id=request.id,
            request_type=request.request_type.value,
            status=request.status.value,
            sla_due_at=request.sla_due_at,
            submitted_at=request.submitted_at,
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/requests",
    response_model=list[RightsRequestResponse],
    summary="List rights requests",
)
async def list_requests(
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: RightsService = Depends(get_rights_service),
) -> list[RightsRequestResponse]:
    requests = service.list_requests(tenant_id=tenant_id, principal_ref=principal_ref)
    return [
        RightsRequestResponse(
            id=r.id,
            request_type=r.request_type.value,
            status=r.status.value,
            sla_due_at=r.sla_due_at,
            submitted_at=r.submitted_at,
            resolved_at=r.resolved_at,
        )
        for r in requests
    ]


@router.post(
    "/grievances",
    response_model=GrievanceResponse,
    summary="Submit a grievance",
)
async def submit_grievance(
    body: GrievanceCreate,
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: RightsService = Depends(get_rights_service),
) -> GrievanceResponse:
    if body.principal_ref != principal_ref:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Principal mismatch")

    try:
        grievance = service.submit_grievance(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            subject=body.subject,
            description=body.description,
        )
        return GrievanceResponse(
            id=grievance.id,
            subject=grievance.subject,
            status=grievance.status.value,
            sla_due_at=grievance.sla_due_at,
            submitted_at=grievance.submitted_at,
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/grievances",
    response_model=list[GrievanceResponse],
    summary="List grievances",
)
async def list_grievances(
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: RightsService = Depends(get_rights_service),
) -> list[GrievanceResponse]:
    grievances = service.list_open_grievances(tenant_id=tenant_id)
    return [
        GrievanceResponse(
            id=g.id,
            subject=g.subject,
            status=g.status.value,
            sla_due_at=g.sla_due_at,
            submitted_at=g.submitted_at,
            resolved_at=g.resolved_at,
        )
        for g in grievances
    ]
