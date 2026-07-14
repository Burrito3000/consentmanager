"""Consent API endpoints — grant, modify, withdraw, query."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from src.api.auth import (
    get_principal_ref_from_token,
    get_tenant_id_from_token,
)
from src.api.schemas import (
    ConsentDetailResponse,
    ConsentEventResponse,
    ConsentGrantRequest,
    ConsentGrantResponse,
    ConsentModifyRequest,
    ConsentResponse,
    ConsentWithdrawRequest,
)
from src.domain.exceptions import (
    ConsentNotFoundError,
    DomainError,
)
from src.services.consent_service import ConsentService
from src.services.container import ServiceContainer

router = APIRouter(prefix="/consent", tags=["Consent"])


def get_consent_service() -> ConsentService:
    container = ServiceContainer()
    return container.consent_service()


@router.post(
    "/grant",
    response_model=ConsentGrantResponse,
    summary="Grant consent for one or more purposes",
    description="DPDP: Per-purpose granular consent with explicit affirmative action. Requires notice_version for informed consent.",
)
async def grant_consent(
    request: Request,
    body: ConsentGrantRequest,
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentGrantResponse:
    # DPDP: principal in path must match token
    if body.principal_ref != principal_ref:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal mismatch",
        )

    try:
        result = service.grant_consent(
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            purpose_grants=[pg.model_dump() for pg in body.purpose_grants],
            notice_version=body.notice_version,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            expires_at=body.expires_at,
        )
        return ConsentGrantResponse(
            consent_id=result["consent_id"],
            status=result["status"],
            receipt=result["receipt"],
        )
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{consent_id}/modify",
    response_model=ConsentGrantResponse,
    summary="Modify consent preferences",
)
async def modify_consent(
    consent_id: str,
    request: Request,
    body: ConsentModifyRequest,
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentGrantResponse:
    if body.principal_ref != principal_ref:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal mismatch",
        )

    try:
        result = service.modify_consent(
            consent_id=consent_id,
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            purpose_grants=[pg.model_dump() for pg in body.purpose_grants],
            notice_version=body.notice_version,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return ConsentGrantResponse(
            consent_id=result["consent_id"],
            status=result["status"],
            receipt="",
        )
    except ConsentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/{consent_id}/withdraw",
    response_model=ConsentGrantResponse,
    summary="Withdraw consent for all purposes",
    description="DPDP: Withdrawal must be as easy as granting. Fires webhooks to tenant and downstream processors.",
)
async def withdraw_consent(
    consent_id: str,
    request: Request,
    body: ConsentWithdrawRequest,
    tenant_id: str = Depends(get_tenant_id_from_token),
    principal_ref: str = Depends(get_principal_ref_from_token),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentGrantResponse:
    if body.principal_ref != principal_ref:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Principal mismatch",
        )

    try:
        result = service.withdraw_consent(
            consent_id=consent_id,
            tenant_id=tenant_id,
            principal_ref=principal_ref,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return ConsentGrantResponse(
            consent_id=result["consent_id"],
            status=result["status"],
            receipt="",
        )
    except ConsentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found")
    except DomainError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{consent_id}",
    response_model=ConsentDetailResponse,
    summary="Get consent detail with event timeline",
)
async def get_consent(
    consent_id: str,
    tenant_id: str = Depends(get_tenant_id_from_token),
    service: ConsentService = Depends(get_consent_service),
) -> ConsentDetailResponse:
    result = service.get_consent(consent_id=consent_id, tenant_id=tenant_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Consent not found")

    artifact = result["artifact"]
    return ConsentDetailResponse(
        artifact=ConsentResponse(
            consent_id=artifact.consent_id,
            status=artifact.status.value,
            principal_ref=artifact.principal_ref,
            purpose_consents=[
                {
                    "purpose_id": pc.purpose_id,
                    "granted": pc.granted,
                    "data_categories": list(pc.data_categories),
                }
                for pc in artifact.purpose_consents
            ],
            created_at=artifact.created_at,
            modified_at=artifact.modified_at,
            expires_at=artifact.expires_at,
        ),
        current_status=result["current_status"],
        events=[
            ConsentEventResponse(
                event_id=e.event_id,
                event_type=e.event_type,
                timestamp=e.timestamp,
                purpose_consents=[
                    {
                        "purpose_id": pc.purpose_id,
                        "granted": pc.granted,
                        "data_categories": list(pc.data_categories),
                    }
                    for pc in e.purpose_consents
                ],
                ip_address=e.ip_address,
                notice_version=e.notice_version,
            )
            for e in result["events"]
        ],
    )


@router.get(
    "/",
    response_model=list[dict],
    summary="List consents",
)
async def list_consents(
    principal_ref: str | None = Query(None),
    tenant_id: str = Depends(get_tenant_id_from_token),
    service: ConsentService = Depends(get_consent_service),
) -> list[dict]:
    return service.list_consents(tenant_id=tenant_id, principal_ref=principal_ref)
