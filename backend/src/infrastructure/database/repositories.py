"""SQLAlchemy implementations of repository interfaces.

Each repository converts between domain entities and ORM models
using conversion methods.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.api_key import ApiKey
from src.domain.audit import AuditLogEntry
from src.domain.consent import (
    ConsentArtifact,
    ConsentEvent,
    ConsentReceipt,
    ConsentStatus,
    PurposeConsent,
)
from src.domain.notice import Notice, NoticeTranslation
from src.domain.principal import DataPrincipal
from src.domain.purpose import LawfulBasis, Purpose
from src.domain.rights import (
    Grievance,
    GrievanceStatus,
    RightsRequest,
    RightsRequestStatus,
    RightsRequestType,
)
from src.domain.tenant import Tenant
from src.domain.user import User, UserRole
from src.domain.webhook import Webhook, WebhookEvent
from src.infrastructure.database import models
from src.repositories.interfaces import (
    IApiKeyRepository,
    IAuditLogRepository,
    IConsentEventRepository,
    IConsentReceiptRepository,
    IConsentRepository,
    IDataPrincipalRepository,
    IGrievanceRepository,
    INoticeRepository,
    IPurposeRepository,
    IRightsRequestRepository,
    ITenantRepository,
    IUserRepository,
    IWebhookRepository,
)


def _tenant_from_model(m: models.TenantModel) -> Tenant:
    return Tenant(
        id=m.id,
        name=m.name,
        contact_email=m.contact_email,
        supported_languages=tuple(m.supported_languages or ["en"]),
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _purpose_from_model(m: models.PurposeModel) -> Purpose:
    return Purpose(
        id=m.id,
        tenant_id=m.tenant_id,
        name=m.name,
        description=m.description,
        data_categories=tuple(m.data_categories or []),
        retention_period_days=m.retention_period_days,
        lawful_basis=LawfulBasis(m.lawful_basis),
        is_mandatory=m.is_mandatory,
        is_active=m.is_active,
        version=m.version,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _principal_from_model(m: models.DataPrincipalModel) -> DataPrincipal:
    return DataPrincipal(
        id=m.id,
        tenant_id=m.tenant_id,
        external_ref=m.external_ref,
        email=m.email,
        phone=m.phone,
        locale=m.locale,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _consent_artifact_from_model(m: models.ConsentArtifactModel) -> ConsentArtifact:
    pcs = tuple(
        PurposeConsent(
            purpose_id=pc["purpose_id"],
            granted=pc["granted"],
            data_categories=tuple(pc.get("data_categories", [])),
        )
        for pc in (m.purpose_consents or [])
    )
    return ConsentArtifact(
        consent_id=m.consent_id,
        tenant_id=m.tenant_id,
        principal_ref=m.principal_ref,
        purpose_consents=pcs,
        status=ConsentStatus(m.status),
        schema_version=m.schema_version,
        expires_at=m.expires_at,
        signed_artifact=m.signed_artifact,
        created_at=m.created_at,
        modified_at=m.modified_at,
    )


def _consent_event_from_model(m: models.ConsentEventModel) -> ConsentEvent:
    return ConsentEvent(
        event_id=m.event_id,
        consent_id=m.consent_id,
        tenant_id=m.tenant_id,
        event_type=m.event_type,
        purpose_consents=tuple(
            PurposeConsent(
                purpose_id=pc["purpose_id"],
                granted=pc["granted"],
                data_categories=tuple(pc.get("data_categories", [])),
            )
            for pc in (m.purpose_consents or [])
        ),
        timestamp=m.timestamp,
        ip_address=m.ip_address,
        user_agent=m.user_agent,
        notice_version=m.notice_version,
    )


def _notice_from_model(m: models.NoticeModel) -> Notice:
    translations = tuple(
        NoticeTranslation(
            locale=t.locale,
            title=t.title,
            body_text=t.body_text,
            how_to_withdraw=t.how_to_withdraw,
            how_to_complain_to_dpb=t.how_to_complain_to_dpb,
        )
        for t in (m.translations or [])
    )
    return Notice(
        id=m.id,
        purpose_id=m.purpose_id,
        tenant_id=m.tenant_id,
        translations=translations,
        version=m.version,
        is_published=m.is_published,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _rights_from_model(m: models.RightsRequestModel) -> RightsRequest:
    return RightsRequest(
        id=m.id,
        tenant_id=m.tenant_id,
        principal_ref=m.principal_ref,
        request_type=RightsRequestType(m.request_type),
        status=RightsRequestStatus(m.status),
        sla_due_at=m.sla_due_at,
        notes=m.notes,
        submitted_at=m.submitted_at,
        resolved_at=m.resolved_at,
    )


def _grievance_from_model(m: models.GrievanceModel) -> Grievance:
    return Grievance(
        id=m.id,
        tenant_id=m.tenant_id,
        principal_ref=m.principal_ref,
        subject=m.subject,
        description=m.description,
        status=GrievanceStatus(m.status),
        sla_due_at=m.sla_due_at,
        submitted_at=m.submitted_at,
        resolved_at=m.resolved_at,
    )


def _audit_entry_from_model(m: models.AuditLogModel) -> AuditLogEntry:
    return AuditLogEntry(
        entry_id=m.entry_id,
        tenant_id=m.tenant_id,
        prev_hash=m.prev_hash,
        hash_value=m.hash_value,
        payload=m.payload or {},
        action=m.action,
        actor=m.actor,
        timestamp=m.timestamp,
        retention_until=m.retention_until,
    )


def _webhook_from_model(m: models.WebhookModel) -> Webhook:
    return Webhook(
        id=m.id,
        tenant_id=m.tenant_id,
        url=m.url,
        secret=m.secret,
        events=tuple(WebhookEvent(e) for e in (m.events or [])),
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _user_from_model(m: models.UserModel) -> User:
    return User(
        id=m.id,
        tenant_id=m.tenant_id,
        email=m.email,
        password_hash=m.password_hash,
        role=UserRole(m.role),
        is_active=m.is_active,
        created_at=m.created_at,
        updated_at=m.updated_at,
        last_login_at=m.last_login_at,
    )


def _api_key_from_model(m: models.ApiKeyModel) -> ApiKey:
    return ApiKey(
        id=m.id,
        tenant_id=m.tenant_id,
        key_prefix=m.key_prefix,
        key_hash=m.key_hash,
        label=m.label,
        allowed_origins=tuple(m.allowed_origins or []),
        is_active=m.is_active,
        created_at=m.created_at,
        expires_at=m.expires_at,
    )


def _receipt_from_model(m: models.ConsentReceiptModel) -> ConsentReceipt:
    return ConsentReceipt(
        receipt_id=m.receipt_id,
        consent_id=m.consent_id,
        tenant_id=m.tenant_id,
        principal_ref=m.principal_ref,
        receipt_data=m.receipt_data,
        generated_at=m.generated_at,
    )


# ── Repository Implementations ──────────────────────────────────────────────


class SqlTenantRepository(ITenantRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, tenant: Tenant) -> Tenant:
        m = self.session.get(models.TenantModel, tenant.id)
        if m:
            m.name = tenant.name
            m.contact_email = tenant.contact_email
            m.supported_languages = list(tenant.supported_languages)
            m.is_active = tenant.is_active
            m.updated_at = datetime.now(UTC)
        else:
            m = models.TenantModel(
                id=tenant.id,
                name=tenant.name,
                contact_email=tenant.contact_email,
                supported_languages=list(tenant.supported_languages),
                is_active=tenant.is_active,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
            )
            self.session.add(m)
        return tenant

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        m = self.session.get(models.TenantModel, tenant_id)
        return _tenant_from_model(m) if m else None

    def list_all(self) -> list[Tenant]:
        return [
            _tenant_from_model(m)
            for m in self.session.execute(select(models.TenantModel)).scalars()
        ]


class SqlPurposeRepository(IPurposeRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, purpose: Purpose) -> Purpose:
        m = self.session.get(models.PurposeModel, purpose.id)
        if m:
            m.name = purpose.name
            m.description = purpose.description
            m.data_categories = list(purpose.data_categories)
            m.retention_period_days = purpose.retention_period_days
            m.lawful_basis = purpose.lawful_basis.value
            m.is_mandatory = purpose.is_mandatory
            m.is_active = purpose.is_active
            m.version = purpose.version
            m.updated_at = datetime.now(UTC)
        else:
            m = models.PurposeModel(
                id=purpose.id,
                tenant_id=purpose.tenant_id,
                name=purpose.name,
                description=purpose.description,
                data_categories=list(purpose.data_categories),
                retention_period_days=purpose.retention_period_days,
                lawful_basis=purpose.lawful_basis.value,
                is_mandatory=purpose.is_mandatory,
                is_active=purpose.is_active,
                version=purpose.version,
                created_at=purpose.created_at,
                updated_at=purpose.updated_at,
            )
            self.session.add(m)
        return purpose

    def get_by_id(self, purpose_id: str) -> Purpose | None:
        m = self.session.get(models.PurposeModel, purpose_id)
        return _purpose_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[Purpose]:
        stmt = (
            select(models.PurposeModel)
            .where(models.PurposeModel.tenant_id == tenant_id)
            .order_by(models.PurposeModel.created_at.desc())
        )
        return [_purpose_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_active_by_tenant(self, tenant_id: str) -> list[Purpose]:
        stmt = (
            select(models.PurposeModel)
            .where(
                models.PurposeModel.tenant_id == tenant_id,
                models.PurposeModel.is_active,
            )
            .order_by(models.PurposeModel.created_at.desc())
        )
        return [_purpose_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlDataPrincipalRepository(IDataPrincipalRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, principal: DataPrincipal) -> DataPrincipal:
        m = self.session.get(models.DataPrincipalModel, principal.id)
        if m:
            m.email = principal.email
            m.phone = principal.phone
            m.locale = principal.locale
            m.updated_at = datetime.now(UTC)
        else:
            m = models.DataPrincipalModel(
                id=principal.id,
                tenant_id=principal.tenant_id,
                external_ref=principal.external_ref,
                email=principal.email,
                phone=principal.phone,
                locale=principal.locale,
                created_at=principal.created_at,
                updated_at=principal.updated_at,
            )
            self.session.add(m)
        return principal

    def get_by_id(self, principal_id: str) -> DataPrincipal | None:
        m = self.session.get(models.DataPrincipalModel, principal_id)
        return _principal_from_model(m) if m else None

    def get_by_external_ref(self, tenant_id: str, external_ref: str) -> DataPrincipal | None:
        stmt = select(models.DataPrincipalModel).where(
            models.DataPrincipalModel.tenant_id == tenant_id,
            models.DataPrincipalModel.external_ref == external_ref,
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _principal_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[DataPrincipal]:
        stmt = (
            select(models.DataPrincipalModel)
            .where(models.DataPrincipalModel.tenant_id == tenant_id)
            .order_by(models.DataPrincipalModel.created_at.desc())
        )
        return [_principal_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlConsentRepository(IConsentRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, artifact: ConsentArtifact) -> ConsentArtifact:
        m = self.session.get(models.ConsentArtifactModel, artifact.consent_id)
        if m:
            m.purpose_consents = [
                {
                    "purpose_id": pc.purpose_id,
                    "granted": pc.granted,
                    "data_categories": list(pc.data_categories),
                }
                for pc in artifact.purpose_consents
            ]
            m.status = artifact.status.value
            m.signed_artifact = artifact.signed_artifact
            m.modified_at = datetime.now(UTC)
        else:
            m = models.ConsentArtifactModel(
                consent_id=artifact.consent_id,
                tenant_id=artifact.tenant_id,
                principal_ref=artifact.principal_ref,
                purpose_consents=[
                    {
                        "purpose_id": pc.purpose_id,
                        "granted": pc.granted,
                        "data_categories": list(pc.data_categories),
                    }
                    for pc in artifact.purpose_consents
                ],
                status=artifact.status.value,
                schema_version=artifact.schema_version,
                expires_at=artifact.expires_at,
                signed_artifact=artifact.signed_artifact,
                created_at=artifact.created_at,
                modified_at=artifact.modified_at,
            )
            self.session.add(m)
        return artifact

    def get_by_id(self, consent_id: str) -> ConsentArtifact | None:
        m = self.session.get(models.ConsentArtifactModel, consent_id)
        return _consent_artifact_from_model(m) if m else None

    def list_by_principal(self, tenant_id: str, principal_ref: str) -> list[ConsentArtifact]:
        stmt = (
            select(models.ConsentArtifactModel)
            .where(
                models.ConsentArtifactModel.tenant_id == tenant_id,
                models.ConsentArtifactModel.principal_ref == principal_ref,
            )
            .order_by(models.ConsentArtifactModel.created_at.desc())
        )
        return [_consent_artifact_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_by_tenant(self, tenant_id: str) -> list[ConsentArtifact]:
        stmt = (
            select(models.ConsentArtifactModel)
            .where(models.ConsentArtifactModel.tenant_id == tenant_id)
            .order_by(models.ConsentArtifactModel.created_at.desc())
        )
        return [_consent_artifact_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_active_by_tenant(self, tenant_id: str) -> list[ConsentArtifact]:
        stmt = (
            select(models.ConsentArtifactModel)
            .where(
                models.ConsentArtifactModel.tenant_id == tenant_id,
                models.ConsentArtifactModel.status == ConsentStatus.ACTIVE.value,
            )
            .order_by(models.ConsentArtifactModel.created_at.desc())
        )
        return [_consent_artifact_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlConsentEventRepository(IConsentEventRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, event: ConsentEvent) -> ConsentEvent:
        m = models.ConsentEventModel(
            event_id=event.event_id,
            consent_id=event.consent_id,
            tenant_id=event.tenant_id,
            event_type=event.event_type,
            purpose_consents=[
                {
                    "purpose_id": pc.purpose_id,
                    "granted": pc.granted,
                    "data_categories": list(pc.data_categories),
                }
                for pc in event.purpose_consents
            ],
            timestamp=event.timestamp,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            notice_version=event.notice_version,
        )
        self.session.add(m)
        return event

    def list_by_consent(self, consent_id: str) -> list[ConsentEvent]:
        stmt = (
            select(models.ConsentEventModel)
            .where(models.ConsentEventModel.consent_id == consent_id)
            .order_by(models.ConsentEventModel.timestamp.asc())
        )
        return [_consent_event_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_by_tenant(self, tenant_id: str) -> list[ConsentEvent]:
        stmt = (
            select(models.ConsentEventModel)
            .where(models.ConsentEventModel.tenant_id == tenant_id)
            .order_by(models.ConsentEventModel.timestamp.desc())
        )
        return [_consent_event_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlNoticeRepository(INoticeRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, notice: Notice) -> Notice:
        m = self.session.get(models.NoticeModel, notice.id)
        if m:
            m.is_published = notice.is_published
            m.version = notice.version
            m.updated_at = datetime.now(UTC)
            self.session.query(models.NoticeTranslationModel).filter_by(
                notice_id=notice.id
            ).delete()
        else:
            m = models.NoticeModel(
                id=notice.id,
                purpose_id=notice.purpose_id,
                tenant_id=notice.tenant_id,
                version=notice.version,
                is_published=notice.is_published,
                created_at=notice.created_at,
                updated_at=notice.updated_at,
            )
            self.session.add(m)

        for t in notice.translations:
            self.session.add(
                models.NoticeTranslationModel(
                    notice_id=m.id,
                    locale=t.locale,
                    title=t.title,
                    body_text=t.body_text,
                    how_to_withdraw=t.how_to_withdraw,
                    how_to_complain_to_dpb=t.how_to_complain_to_dpb,
                )
            )
        return notice

    def get_by_id(self, notice_id: str) -> Notice | None:
        m = self.session.get(models.NoticeModel, notice_id)
        return _notice_from_model(m) if m else None

    def list_by_purpose(self, purpose_id: str) -> list[Notice]:
        stmt = (
            select(models.NoticeModel)
            .where(models.NoticeModel.purpose_id == purpose_id)
            .order_by(models.NoticeModel.version.desc())
        )
        return [_notice_from_model(m) for m in self.session.execute(stmt).scalars()]

    def get_latest_by_purpose(self, purpose_id: str) -> Notice | None:
        stmt = (
            select(models.NoticeModel)
            .where(models.NoticeModel.purpose_id == purpose_id)
            .order_by(models.NoticeModel.version.desc())
            .limit(1)
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _notice_from_model(m) if m else None

    def get_published_by_purpose(self, purpose_id: str) -> Notice | None:
        stmt = (
            select(models.NoticeModel)
            .where(
                models.NoticeModel.purpose_id == purpose_id,
                models.NoticeModel.is_published,
            )
            .order_by(models.NoticeModel.version.desc())
            .limit(1)
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _notice_from_model(m) if m else None


class SqlRightsRequestRepository(IRightsRequestRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, request: RightsRequest) -> RightsRequest:
        m = self.session.get(models.RightsRequestModel, request.id)
        if m:
            m.status = request.status.value
            m.notes = request.notes
            m.resolved_at = request.resolved_at
        else:
            m = models.RightsRequestModel(
                id=request.id,
                tenant_id=request.tenant_id,
                principal_ref=request.principal_ref,
                request_type=request.request_type.value,
                status=request.status.value,
                sla_due_at=request.sla_due_at,
                notes=request.notes,
                submitted_at=request.submitted_at,
                resolved_at=request.resolved_at,
            )
            self.session.add(m)
        return request

    def get_by_id(self, request_id: str) -> RightsRequest | None:
        m = self.session.get(models.RightsRequestModel, request_id)
        return _rights_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[RightsRequest]:
        stmt = (
            select(models.RightsRequestModel)
            .where(models.RightsRequestModel.tenant_id == tenant_id)
            .order_by(models.RightsRequestModel.submitted_at.desc())
        )
        return [_rights_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_by_principal(self, tenant_id: str, principal_ref: str) -> list[RightsRequest]:
        stmt = (
            select(models.RightsRequestModel)
            .where(
                models.RightsRequestModel.tenant_id == tenant_id,
                models.RightsRequestModel.principal_ref == principal_ref,
            )
            .order_by(models.RightsRequestModel.submitted_at.desc())
        )
        return [_rights_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_pending(self, tenant_id: str) -> list[RightsRequest]:
        stmt = (
            select(models.RightsRequestModel)
            .where(
                models.RightsRequestModel.tenant_id == tenant_id,
                models.RightsRequestModel.status.in_(["SUBMITTED", "IN_PROGRESS"]),
            )
            .order_by(models.RightsRequestModel.sla_due_at.asc())
        )
        return [_rights_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlGrievanceRepository(IGrievanceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, grievance: Grievance) -> Grievance:
        m = self.session.get(models.GrievanceModel, grievance.id)
        if m:
            m.status = grievance.status.value
            m.resolved_at = grievance.resolved_at
        else:
            m = models.GrievanceModel(
                id=grievance.id,
                tenant_id=grievance.tenant_id,
                principal_ref=grievance.principal_ref,
                subject=grievance.subject,
                description=grievance.description,
                status=grievance.status.value,
                sla_due_at=grievance.sla_due_at,
                submitted_at=grievance.submitted_at,
                resolved_at=grievance.resolved_at,
            )
            self.session.add(m)
        return grievance

    def get_by_id(self, grievance_id: str) -> Grievance | None:
        m = self.session.get(models.GrievanceModel, grievance_id)
        return _grievance_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[Grievance]:
        stmt = (
            select(models.GrievanceModel)
            .where(models.GrievanceModel.tenant_id == tenant_id)
            .order_by(models.GrievanceModel.submitted_at.desc())
        )
        return [_grievance_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_open(self, tenant_id: str) -> list[Grievance]:
        stmt = (
            select(models.GrievanceModel)
            .where(
                models.GrievanceModel.tenant_id == tenant_id,
                models.GrievanceModel.status.in_(["OPEN", "ACKNOWLEDGED", "INVESTIGATING"]),
            )
            .order_by(models.GrievanceModel.sla_due_at.asc())
        )
        return [_grievance_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlAuditLogRepository(IAuditLogRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, entry: AuditLogEntry) -> AuditLogEntry:
        m = models.AuditLogModel(
            entry_id=entry.entry_id,
            tenant_id=entry.tenant_id,
            prev_hash=entry.prev_hash,
            hash_value=entry.hash_value,
            payload=entry.payload,
            action=entry.action,
            actor=entry.actor,
            timestamp=entry.timestamp,
            retention_until=entry.retention_until,
        )
        self.session.add(m)
        return entry

    def get_by_id(self, entry_id: str) -> AuditLogEntry | None:
        m = self.session.get(models.AuditLogModel, entry_id)
        return _audit_entry_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[AuditLogEntry]:
        stmt = (
            select(models.AuditLogModel)
            .where(models.AuditLogModel.tenant_id == tenant_id)
            .order_by(models.AuditLogModel.timestamp.desc())
        )
        return [_audit_entry_from_model(m) for m in self.session.execute(stmt).scalars()]

    def get_latest(self, tenant_id: str) -> AuditLogEntry | None:
        stmt = (
            select(models.AuditLogModel)
            .where(models.AuditLogModel.tenant_id == tenant_id)
            .order_by(models.AuditLogModel.timestamp.desc())
            .limit(1)
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _audit_entry_from_model(m) if m else None

    def verify_chain(self, tenant_id: str) -> bool:
        from src.domain.audit import verify_chain as domain_verify

        entries = self.list_by_tenant(tenant_id)
        valid, _ = domain_verify(entries)
        return valid


class SqlWebhookRepository(IWebhookRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, webhook: Webhook) -> Webhook:
        m = self.session.get(models.WebhookModel, webhook.id)
        if m:
            m.url = webhook.url
            m.secret = webhook.secret
            m.events = [e.value for e in webhook.events]
            m.is_active = webhook.is_active
            m.updated_at = datetime.now(UTC)
        else:
            m = models.WebhookModel(
                id=webhook.id,
                tenant_id=webhook.tenant_id,
                url=webhook.url,
                secret=webhook.secret,
                events=[e.value for e in webhook.events],
                is_active=webhook.is_active,
                created_at=webhook.created_at,
                updated_at=webhook.updated_at,
            )
            self.session.add(m)
        return webhook

    def get_by_id(self, webhook_id: str) -> Webhook | None:
        m = self.session.get(models.WebhookModel, webhook_id)
        return _webhook_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[Webhook]:
        stmt = (
            select(models.WebhookModel)
            .where(models.WebhookModel.tenant_id == tenant_id)
            .order_by(models.WebhookModel.created_at.desc())
        )
        return [_webhook_from_model(m) for m in self.session.execute(stmt).scalars()]

    def list_active_by_tenant(self, tenant_id: str) -> list[Webhook]:
        stmt = select(models.WebhookModel).where(
            models.WebhookModel.tenant_id == tenant_id,
            models.WebhookModel.is_active,
        )
        return [_webhook_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlUserRepository(IUserRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, user: User) -> User:
        m = self.session.get(models.UserModel, user.id)
        if m:
            m.email = user.email
            m.password_hash = user.password_hash
            m.role = user.role.value
            m.is_active = user.is_active
            m.last_login_at = user.last_login_at
            m.updated_at = datetime.now(UTC)
        else:
            m = models.UserModel(
                id=user.id,
                tenant_id=user.tenant_id,
                email=user.email,
                password_hash=user.password_hash,
                role=user.role.value,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                last_login_at=user.last_login_at,
            )
            self.session.add(m)
        return user

    def get_by_id(self, user_id: str) -> User | None:
        m = self.session.get(models.UserModel, user_id)
        return _user_from_model(m) if m else None

    def get_by_email(self, tenant_id: str, email: str) -> User | None:
        stmt = select(models.UserModel).where(
            models.UserModel.tenant_id == tenant_id,
            models.UserModel.email == email,
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _user_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[User]:
        stmt = (
            select(models.UserModel)
            .where(models.UserModel.tenant_id == tenant_id)
            .order_by(models.UserModel.created_at.desc())
        )
        return [_user_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlApiKeyRepository(IApiKeyRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, api_key: ApiKey) -> ApiKey:
        m = self.session.get(models.ApiKeyModel, api_key.id)
        if m:
            m.label = api_key.label
            m.allowed_origins = list(api_key.allowed_origins)
            m.is_active = api_key.is_active
            m.expires_at = api_key.expires_at
        else:
            m = models.ApiKeyModel(
                id=api_key.id,
                tenant_id=api_key.tenant_id,
                key_prefix=api_key.key_prefix,
                key_hash=api_key.key_hash,
                label=api_key.label,
                allowed_origins=list(api_key.allowed_origins),
                is_active=api_key.is_active,
                created_at=api_key.created_at,
                expires_at=api_key.expires_at,
            )
            self.session.add(m)
        return api_key

    def get_by_id(self, key_id: str) -> ApiKey | None:
        m = self.session.get(models.ApiKeyModel, key_id)
        return _api_key_from_model(m) if m else None

    def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        stmt = select(models.ApiKeyModel).where(models.ApiKeyModel.key_prefix == key_prefix)
        m = self.session.execute(stmt).scalar_one_or_none()
        return _api_key_from_model(m) if m else None

    def list_by_tenant(self, tenant_id: str) -> list[ApiKey]:
        stmt = (
            select(models.ApiKeyModel)
            .where(models.ApiKeyModel.tenant_id == tenant_id)
            .order_by(models.ApiKeyModel.created_at.desc())
        )
        return [_api_key_from_model(m) for m in self.session.execute(stmt).scalars()]


class SqlConsentReceiptRepository(IConsentReceiptRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(self, receipt: ConsentReceipt) -> ConsentReceipt:
        m = models.ConsentReceiptModel(
            receipt_id=receipt.receipt_id,
            consent_id=receipt.consent_id,
            tenant_id=receipt.tenant_id,
            principal_ref=receipt.principal_ref,
            receipt_data=receipt.receipt_data,
            generated_at=receipt.generated_at,
        )
        self.session.add(m)
        return receipt

    def get_by_id(self, receipt_id: str) -> ConsentReceipt | None:
        m = self.session.get(models.ConsentReceiptModel, receipt_id)
        return _receipt_from_model(m) if m else None

    def get_by_consent(self, consent_id: str) -> ConsentReceipt | None:
        stmt = (
            select(models.ConsentReceiptModel)
            .where(models.ConsentReceiptModel.consent_id == consent_id)
            .limit(1)
        )
        m = self.session.execute(stmt).scalar_one_or_none()
        return _receipt_from_model(m) if m else None
