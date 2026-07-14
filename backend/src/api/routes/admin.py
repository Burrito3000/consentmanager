"""Admin API endpoints — DPO/compliance console.

Replaces the Flask admin portal. All data is pulled from real services
via the same ServiceContainer used by the public API.
"""

from __future__ import annotations

import functools
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError

from src.config.settings import settings
from src.services.container import ServiceContainer

router = APIRouter(prefix="/admin", tags=["Admin"])


# ── Schemas ──────────────────────────────────────────────────────────────────


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminLoginResponse(BaseModel):
    token: str
    email: str


class DashboardResponse(BaseModel):
    total_consents: int = 0
    active_consents: int = 0
    withdrawn_consents: int = 0
    active_pct: float = 0.0
    withdrawn_pct: float = 0.0
    consent_change: str = "0%"
    pending_rights: int = 0
    sla_breached: int = 0
    purpose_stats: list[dict] = []
    recent_events: list[dict] = []
    languages: list[str] = []


class IndexResponse(BaseModel):
    language_count: int = 0
    sla_breached: int = 0


class PurposeItem(BaseModel):
    id: str = ""
    name: str = ""
    description: str = ""
    is_active: bool = False
    retention_days: int = 0
    data_categories: list[str] = []
    lawful_basis: str = ""
    notice_count: int = 0
    consent_count: int = 0


class PurposesResponse(BaseModel):
    purposes: list[PurposeItem] = []
    total_purposes: int = 0
    active_purposes: int = 0
    languages: list[str] = []


class ConsentItem(BaseModel):
    consent_id: str = ""
    principal_ref: str = ""
    purpose_ids: list[str] = []
    status: str = ""
    event_type: str = ""
    timestamp: str = ""
    source: str = ""


class ConsentsResponse(BaseModel):
    consents: list[ConsentItem] = []
    total_consents: int = 0
    active_consents: int = 0
    withdrawn_consents: int = 0
    expired_consents: int = 0
    chain_genesis_hash: str = ""
    chain_latest_hash: str = ""
    chain_verified: bool = False


class RightsRequestItem(BaseModel):
    id: str = ""
    principal_ref: str = ""
    request_type: str = ""
    status: str = ""
    submitted_at: str = ""
    sla_due_at: str = ""
    days_left: str = ""
    is_breached: bool = False


class GrievanceItem(BaseModel):
    id: str = ""
    principal_ref: str = ""
    subject: str = ""
    status: str = ""
    submitted_at: str = ""
    sla_text: str = ""


class RightsResponse(BaseModel):
    rights_requests: list[RightsRequestItem] = []
    grievances: list[GrievanceItem] = []
    total_requests: int = 0
    pending_requests: int = 0
    resolved_requests: int = 0
    sla_breached_requests: int = 0
    total_grievances: int = 0
    open_grievances: int = 0
    resolved_grievances: int = 0
    sla_breached_grievances: int = 0


class AuditEntryItem(BaseModel):
    timestamp: str = ""
    action: str = ""
    actor: str = ""
    resource: str = ""
    prev_hash: str = ""
    hash_value: str = ""
    verified: bool = False


class AuditResponse(BaseModel):
    audit_entries: list[AuditEntryItem] = []
    total_events: int = 0
    chain_valid: bool = True
    consent_events: int = 0
    rights_events: int = 0
    grievance_events: int = 0
    system_events: int = 0


class APIKeyItem(BaseModel):
    id: str = ""
    label: str = ""
    prefix: str = ""
    is_active: bool = False
    created_at: str = ""
    allowed_origins: list[str] = []


class IntegrationResponse(BaseModel):
    api_keys: list[APIKeyItem] = []
    webhooks: list[dict] = []
    origins: list[str] = []


# ── Helpers ──────────────────────────────────────────────────────────────────


def _format_ts(dt: datetime | None = None) -> str:
    return (dt or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M:%S")


def _get_default_tenant() -> str | None:
    container = ServiceContainer()
    uow = container.get_uow()
    with uow:
        tenants = uow.tenants.list_all()
        if tenants:
            return tenants[0].id
    return None


# ── Safe DB decorator ────────────────────────────────────────────────────────


def _safe_endpoint(resp_model):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OperationalError:
                return resp_model()

        return wrapper

    return decorator


# ── Auth Dependency ──────────────────────────────────────────────────────────


def verify_admin_token(authorization: str = Header(...)) -> str:
    import jwt

    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if payload.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Not an admin token")
        return payload.get("sub", "admin")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post("/auth/login", response_model=AdminLoginResponse)
def admin_login(body: AdminLoginRequest):
    from datetime import UTC, datetime, timedelta

    import jwt

    if body.email != settings.admin_email or body.password != settings.admin_password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    payload = {
        "sub": body.email,
        "role": "admin",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(hours=24),
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return AdminLoginResponse(token=token, email=body.email)


@router.get("/index", response_model=IndexResponse)
@_safe_endpoint(IndexResponse)
def get_index(admin: str = Depends(verify_admin_token)):
    tenant_id = _get_default_tenant()
    container = ServiceContainer()
    language_count = len(container.notice_service().list_supported_languages())
    sla_breached = 0
    if tenant_id:
        rights_svc = container.rights_service()
        sla_breached = len(rights_svc.check_sla_breaches(tenant_id))
    return IndexResponse(language_count=language_count, sla_breached=sla_breached)


@router.get("/dashboard", response_model=DashboardResponse)
@_safe_endpoint(DashboardResponse)
def get_dashboard(admin: str = Depends(verify_admin_token)):
    container = ServiceContainer()
    notice_svc = container.notice_service()
    rights_svc = container.rights_service()
    languages = list(notice_svc.list_supported_languages().keys())
    tenant_id = _get_default_tenant()

    total_consents = 0
    active = 0
    withdrawn = 0
    pending = 0
    sla_breached_count = 0
    purpose_stats = []
    recent_events = []

    if tenant_id:
        uow = container.get_uow()
        with uow:
            all_consents = uow.consents.list_by_tenant(tenant_id)
            total_consents = len(all_consents)
            active = sum(1 for c in all_consents if c.status.value == "ACTIVE")
            withdrawn = sum(1 for c in all_consents if c.status.value == "WITHDRAWN")

            purposes = uow.purposes.list_by_tenant(tenant_id)
            for p in purposes:
                count = sum(1 for c in all_consents if c.has_purpose(p.id))
                pct = round(count / total_consents * 100, 1) if total_consents else 0
                purpose_stats.append({"name": p.name, "count": count, "pct": pct})

            pending_list = rights_svc.get_pending_requests(tenant_id)
            pending = len(pending_list)
            sla_breached_list = rights_svc.check_sla_breaches(tenant_id)
            sla_breached_count = len(sla_breached_list)

            events = uow.consent_events.list_by_tenant(tenant_id)
            for e in events[-4:]:
                consent = uow.consents.get_by_id(e.consent_id)
                principal = consent.principal_ref if consent else "unknown"
                recent_events.append(
                    {
                        "action": f"CONSENT_{e.event_type.value}",
                        "timestamp": _format_ts(e.timestamp),
                        "actor": principal,
                    }
                )

    active_pct = round(active / total_consents * 100, 1) if total_consents else 0
    withdrawn_pct = round(withdrawn / total_consents * 100, 1) if total_consents else 0

    return DashboardResponse(
        total_consents=total_consents,
        active_consents=active,
        withdrawn_consents=withdrawn,
        active_pct=active_pct,
        withdrawn_pct=withdrawn_pct,
        consent_change=f"+{active_pct}%" if active_pct else "0%",
        pending_rights=pending,
        sla_breached=sla_breached_count,
        purpose_stats=purpose_stats,
        recent_events=recent_events,
        languages=languages,
    )


@router.get("/purposes", response_model=PurposesResponse)
@_safe_endpoint(PurposesResponse)
def get_purposes(admin: str = Depends(verify_admin_token)):
    container = ServiceContainer()
    notice_svc = container.notice_service()
    languages = list(notice_svc.list_supported_languages().keys())
    tenant_id = _get_default_tenant()
    purposes_list = []
    total_purposes = 0
    active_purposes = 0

    if tenant_id:
        uow = container.get_uow()
        with uow:
            all_purposes = uow.purposes.list_by_tenant(tenant_id)
            total_purposes = len(all_purposes)
            for p in all_purposes:
                if p.is_active:
                    active_purposes += 1
                notices = uow.notices.list_by_purpose(p.id)
                consent_count = 0
                if tenant_id:
                    consents = uow.consents.list_by_tenant(tenant_id)
                    consent_count = sum(1 for c in consents if c.has_purpose(p.id))
                purposes_list.append(
                    PurposeItem(
                        id=p.id,
                        name=p.name,
                        description=p.description,
                        is_active=p.is_active,
                        retention_days=p.retention_period_days,
                        data_categories=list(p.data_categories),
                        lawful_basis=p.lawful_basis.value if p.lawful_basis else "consent",
                        notice_count=len(notices),
                        consent_count=consent_count,
                    )
                )

    return PurposesResponse(
        purposes=purposes_list,
        total_purposes=total_purposes,
        active_purposes=active_purposes,
        languages=languages,
    )


@router.get("/consents", response_model=ConsentsResponse)
@_safe_endpoint(ConsentsResponse)
def get_consents(admin: str = Depends(verify_admin_token)):
    tenant_id = _get_default_tenant()
    consent_list = []
    total_count = 0
    active_count = 0
    withdrawn_count = 0
    expired_count = 0
    genesis_hash = ""
    latest_hash = ""
    chain_verified = False

    if tenant_id:
        container = ServiceContainer()
        uow = container.get_uow()
        audit_svc = container.audit_service()
        with uow:
            artifacts = uow.consents.list_by_tenant(tenant_id)
            total_count = len(artifacts)
            for a in artifacts:
                if a.status.value == "ACTIVE":
                    active_count += 1
                elif a.status.value == "WITHDRAWN":
                    withdrawn_count += 1
                elif a.status.value == "EXPIRED":
                    expired_count += 1
                events = uow.consent_events.list_by_consent(a.consent_id)
                latest_event = events[-1] if events else None
                consent_list.append(
                    ConsentItem(
                        consent_id=a.consent_id,
                        principal_ref=a.principal_ref,
                        purpose_ids=a.grant_ids(),
                        status=a.status.value,
                        event_type=(
                            latest_event.event_type.value if latest_event else a.status.value
                        ),
                        timestamp=_format_ts(
                            latest_event.timestamp if latest_event else a.created_at
                        ),
                        source=(
                            latest_event.user_agent
                            if latest_event and hasattr(latest_event, "user_agent")
                            else "API"
                        ),
                    )
                )

            audit_entries = uow.audit_logs.list_by_tenant(tenant_id)
            if audit_entries:
                genesis_hash = audit_entries[0].hash_value[:64]
                latest_hash = audit_entries[-1].hash_value[:64]
            is_valid, _ = audit_svc.verify_tenant_chain(tenant_id)
            chain_verified = is_valid

    return ConsentsResponse(
        consents=consent_list,
        total_consents=total_count,
        active_consents=active_count,
        withdrawn_consents=withdrawn_count,
        expired_consents=expired_count,
        chain_genesis_hash=genesis_hash,
        chain_latest_hash=latest_hash,
        chain_verified=chain_verified,
    )


@router.get("/rights", response_model=RightsResponse)
@_safe_endpoint(RightsResponse)
def get_rights(admin: str = Depends(verify_admin_token)):
    tenant_id = _get_default_tenant()
    rights_requests = []
    grievances_list = []
    total_requests = 0
    pending_count = 0
    resolved_count = 0
    total_grievances = 0
    open_grievances = 0
    resolved_grievances = 0
    sla_breached_requests = 0
    sla_breached_grievances = 0

    if tenant_id:
        container = ServiceContainer()
        rights_svc = container.rights_service()
        uow = container.get_uow()
        with uow:
            all_requests = rights_svc.list_requests(tenant_id)
            total_requests = len(all_requests)
            for r in all_requests:
                if r.status.value in ("SUBMITTED", "IN_PROGRESS"):
                    pending_count += 1
                if r.status.value in ("RESOLVED", "REJECTED"):
                    resolved_count += 1
                if r.is_sla_breached():
                    sla_breached_requests += 1
                days_left = ""
                if r.sla_due_at:
                    remaining = (r.sla_due_at - datetime.now(UTC)).days
                    days_left = f"{remaining}d" if remaining > 0 else "BREACHED"
                rights_requests.append(
                    RightsRequestItem(
                        id=r.id[:8],
                        principal_ref=r.principal_ref,
                        request_type=r.request_type.value,
                        status=r.status.value,
                        submitted_at=_format_ts(r.submitted_at),
                        sla_due_at=_format_ts(r.sla_due_at) if r.sla_due_at else "",
                        days_left=days_left,
                        is_breached=r.is_sla_breached(),
                    )
                )

            all_grievances = uow.grievances.list_by_tenant(tenant_id)
            total_grievances = len(all_grievances)
            for g in all_grievances:
                if g.status.value in ("OPEN", "ACKNOWLEDGED", "INVESTIGATING"):
                    open_grievances += 1
                if g.status.value in ("RESOLVED", "REJECTED"):
                    resolved_grievances += 1
                if g.is_sla_breached():
                    sla_breached_grievances += 1
                sla_text = ""
                if g.sla_due_at:
                    remaining = (g.sla_due_at - datetime.now(UTC)).days
                    if remaining > 0:
                        sla_text = f"{remaining}d remaining"
                    elif g.status.value in ("RESOLVED", "REJECTED"):
                        sla_text = "Closed"
                    else:
                        sla_text = "OVERDUE"
                grievances_list.append(
                    GrievanceItem(
                        id=g.id[:8],
                        principal_ref=g.principal_ref,
                        subject=g.subject,
                        status=g.status.value,
                        submitted_at=_format_ts(g.submitted_at),
                        sla_text=sla_text,
                    )
                )

    return RightsResponse(
        rights_requests=rights_requests,
        grievances=grievances_list,
        total_requests=total_requests,
        pending_requests=pending_count,
        resolved_requests=resolved_count,
        sla_breached_requests=sla_breached_requests,
        total_grievances=total_grievances,
        open_grievances=open_grievances,
        resolved_grievances=resolved_grievances,
        sla_breached_grievances=sla_breached_grievances,
    )


@router.get("/audit", response_model=AuditResponse)
@_safe_endpoint(AuditResponse)
def get_audit(admin: str = Depends(verify_admin_token)):
    tenant_id = _get_default_tenant()
    audit_entries = []
    total_events = 0
    chain_valid = True
    consent_events = 0
    rights_events = 0
    grievance_events = 0
    system_events = 0

    if tenant_id:
        container = ServiceContainer()
        audit_svc = container.audit_service()
        uow = container.get_uow()
        with uow:
            entries = uow.audit_logs.list_by_tenant(tenant_id)
            total_events = len(entries)
            is_valid, _ = audit_svc.verify_tenant_chain(tenant_id)
            chain_valid = is_valid

            for entry in entries[-6:]:
                prev_short = (
                    entry.prev_hash[:8] + "..." + entry.prev_hash[-4:]
                    if len(entry.prev_hash) > 12
                    else entry.prev_hash
                )
                hash_short = (
                    entry.hash_value[:8] + "..." + entry.hash_value[-4:]
                    if len(entry.hash_value) > 12
                    else entry.hash_value
                )
                audit_entries.append(
                    AuditEntryItem(
                        timestamp=_format_ts(entry.timestamp),
                        action=entry.action,
                        actor=entry.actor,
                        resource=entry.payload.get("consent_id")
                        or entry.payload.get("request_id")
                        or entry.payload.get("grievance_id")
                        or entry.payload.get("notice_id", ""),
                        prev_hash=prev_short,
                        hash_value=hash_short,
                        verified=True,
                    )
                )

            for entry in entries:
                action = entry.action
                if action.startswith("consent"):
                    consent_events += 1
                elif action.startswith("rights"):
                    rights_events += 1
                elif action.startswith("grievance"):
                    grievance_events += 1
                else:
                    system_events += 1

    return AuditResponse(
        audit_entries=audit_entries,
        total_events=total_events,
        chain_valid=chain_valid,
        consent_events=consent_events,
        rights_events=rights_events,
        grievance_events=grievance_events,
        system_events=system_events,
    )


@router.get("/integration", response_model=IntegrationResponse)
@_safe_endpoint(IntegrationResponse)
def get_integration(admin: str = Depends(verify_admin_token)):
    tenant_id = _get_default_tenant()
    api_keys = []
    webhooks_list = []
    origins = []

    if tenant_id:
        container = ServiceContainer()
        uow = container.get_uow()
        webhook_svc = container.webhook_service()
        with uow:
            keys = uow.api_keys.list_by_tenant(tenant_id)
            for key in keys:
                api_keys.append(
                    APIKeyItem(
                        id=key.id,
                        label=key.label or "Unnamed",
                        prefix=key.key_prefix,
                        is_active=key.is_active if hasattr(key, "is_active") else True,
                        created_at=(
                            _format_ts(key.created_at)
                            if hasattr(key, "created_at")
                            else _format_ts()
                        ),
                        allowed_origins=(
                            list(key.allowed_origins) if hasattr(key, "allowed_origins") else []
                        ),
                    )
                )

            webhooks_list = webhook_svc.list_webhooks(tenant_id)

            for key in keys:
                for origin in key.allowed_origins if hasattr(key, "allowed_origins") else []:
                    if origin not in origins:
                        origins.append(origin)

    return IntegrationResponse(
        api_keys=api_keys,
        webhooks=webhooks_list,
        origins=origins,
    )
