"""SQLAlchemy 2.0 ORM models for all domain entities.

All tables carry tenant_id for multi-tenant scoping.
Consent is append-only via events; the artifact table is a projection.
Audit log is hash-chained.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.domain.consent import ConsentStatus
from src.domain.purpose import LawfulBasis
from src.domain.rights import GrievanceStatus, RightsRequestStatus
from src.domain.user import UserRole


class Base(DeclarativeBase):
    pass


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return uuid.uuid4().hex


# ─── Tenant ───────────────────────────────────────────────────────────────────


class TenantModel(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    supported_languages: Mapped[dict] = mapped_column(JSON, default=lambda: ["en"])
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# ─── Purpose ──────────────────────────────────────────────────────────────────


class PurposeModel(Base):
    __tablename__ = "purposes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    data_categories: Mapped[dict] = mapped_column(JSON, default=list)
    retention_period_days: Mapped[int] = mapped_column(Integer, nullable=False)
    lawful_basis: Mapped[str] = mapped_column(String(50), default=LawfulBasis.CONSENT.value)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (Index("ix_purposes_tenant_active", "tenant_id", "is_active"),)


# ─── Data Principal ───────────────────────────────────────────────────────────


class DataPrincipalModel(Base):
    __tablename__ = "data_principals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    external_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    locale: Mapped[str] = mapped_column(String(10), default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    __table_args__ = (
        UniqueConstraint("tenant_id", "external_ref", name="uq_principal_external_ref"),
        Index("ix_principals_tenant_ref", "tenant_id", "external_ref"),
    )


# ─── Consent Artifact ─────────────────────────────────────────────────────────


class ConsentArtifactModel(Base):
    """Projection of the latest consent state. Never updated directly."""

    __tablename__ = "consent_artifacts"

    consent_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    principal_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose_consents: Mapped[dict] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(20), default=ConsentStatus.ACTIVE.value, index=True)
    schema_version: Mapped[str] = mapped_column(String(10), default="1.0")
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signed_artifact: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    __table_args__ = (
        Index("ix_consent_tenant_principal", "tenant_id", "principal_ref"),
        Index("ix_consent_tenant_status", "tenant_id", "status"),
    )


# ─── Consent Event (append-only) ─────────────────────────────────────────────


class ConsentEventModel(Base):
    """Append-only event log. Immutable once written."""

    __tablename__ = "consent_events"

    event_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    consent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("consent_artifacts.consent_id"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    purpose_consents: Mapped[dict] = mapped_column(JSON, default=list)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, index=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notice_version: Mapped[str | None] = mapped_column(String(50), nullable=True)

    __table_args__ = (Index("ix_consent_events_consent_ts", "consent_id", "timestamp"),)


# ─── Notice ───────────────────────────────────────────────────────────────────


class NoticeTranslationModel(Base):
    """Multilingual notice translation."""

    __tablename__ = "notice_translations"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    notice_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("notices.id"), nullable=False, index=True
    )
    locale: Mapped[str] = mapped_column(String(10), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    how_to_withdraw: Mapped[str] = mapped_column(Text, nullable=False)
    how_to_complain_to_dpb: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (UniqueConstraint("notice_id", "locale", name="uq_notice_translation_locale"),)


class NoticeModel(Base):
    __tablename__ = "notices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    purpose_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("purposes.id"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    translations = relationship("NoticeTranslationModel", backref="notice", lazy="selectin")

    __table_args__ = (Index("ix_notices_purpose_version", "purpose_id", "version"),)


# ─── Rights Request ───────────────────────────────────────────────────────────


class RightsRequestModel(Base):
    __tablename__ = "rights_requests"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    principal_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    request_type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=RightsRequestStatus.SUBMITTED.value)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_rights_tenant_status", "tenant_id", "status"),)


# ─── Grievance ────────────────────────────────────────────────────────────────


class GrievanceModel(Base):
    __tablename__ = "grievances"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    principal_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=GrievanceStatus.OPEN.value)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_grievances_tenant_status", "tenant_id", "status"),)


# ─── Audit Log ────────────────────────────────────────────────────────────────


class AuditLogModel(Base):
    """Tamper-evident audit log with hash chain."""

    __tablename__ = "audit_logs"

    entry_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    prev_hash: Mapped[str] = mapped_column(String(64), default="")
    hash_value: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    retention_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (Index("ix_audit_tenant_ts", "tenant_id", "timestamp"),)


# ─── Webhook ──────────────────────────────────────────────────────────────────


class WebhookModel(Base):
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(1024), nullable=False)
    secret: Mapped[str] = mapped_column(String(255), nullable=False)
    events: Mapped[dict] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )


# ─── User (Admin RBAC) ────────────────────────────────────────────────────────


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.ANALYST.value)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),)


# ─── API Key ──────────────────────────────────────────────────────────────────


class ApiKeyModel(Base):
    __tablename__ = "api_keys"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    key_prefix: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    key_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    allowed_origins: Mapped[dict] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


# ─── Consent Receipt ──────────────────────────────────────────────────────────


class ConsentReceiptModel(Base):
    __tablename__ = "consent_receipts"

    receipt_id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    consent_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("consent_artifacts.consent_id"), nullable=False, index=True
    )
    tenant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("tenants.id"), nullable=False, index=True
    )
    principal_ref: Mapped[str] = mapped_column(String(255), nullable=False)
    receipt_data: Mapped[str] = mapped_column(Text, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
