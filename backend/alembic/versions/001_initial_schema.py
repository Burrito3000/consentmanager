"""Initial schema — all tables for DPDP CMP.

Revision ID: 001
Revises:
Create Date: 2026-07-13
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "tenants",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=False),
        sa.Column("supported_languages", sa.JSON, nullable=False, server_default='["en"]'),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "purposes",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("data_categories", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("retention_period_days", sa.Integer, nullable=False),
        sa.Column("lawful_basis", sa.String(50), nullable=False, server_default="consent"),
        sa.Column("is_mandatory", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_purposes_tenant_active", "purposes", ["tenant_id", "is_active"])

    op.create_table(
        "data_principals",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("external_ref", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "external_ref", name="uq_principal_external_ref"),
    )
    op.create_index("ix_principals_tenant_ref", "data_principals", ["tenant_id", "external_ref"])

    op.create_table(
        "consent_artifacts",
        sa.Column("consent_id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("principal_ref", sa.String(255), nullable=False),
        sa.Column("purpose_consents", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ACTIVE", index=True),
        sa.Column("schema_version", sa.String(10), nullable=False, server_default="1.0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signed_artifact", sa.Text, nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "modified_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index(
        "ix_consent_tenant_principal", "consent_artifacts", ["tenant_id", "principal_ref"]
    )
    op.create_index("ix_consent_tenant_status", "consent_artifacts", ["tenant_id", "status"])

    op.create_table(
        "consent_events",
        sa.Column("event_id", sa.String(64), primary_key=True),
        sa.Column(
            "consent_id",
            sa.String(64),
            sa.ForeignKey("consent_artifacts.consent_id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("event_type", sa.String(20), nullable=False, index=True),
        sa.Column("purpose_consents", sa.JSON, nullable=False, server_default="[]"),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
            index=True,
        ),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("notice_version", sa.String(50), nullable=True),
    )
    op.create_index("ix_consent_events_consent_ts", "consent_events", ["consent_id", "timestamp"])

    op.create_table(
        "notices",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "purpose_id", sa.String(64), sa.ForeignKey("purposes.id"), nullable=False, index=True
        ),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("version", sa.Integer, nullable=False, server_default="1"),
        sa.Column("is_published", sa.Boolean, nullable=False, server_default="false"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )
    op.create_index("ix_notices_purpose_version", "notices", ["purpose_id", "version"])

    op.create_table(
        "notice_translations",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "notice_id", sa.String(64), sa.ForeignKey("notices.id"), nullable=False, index=True
        ),
        sa.Column("locale", sa.String(10), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("how_to_withdraw", sa.Text, nullable=False),
        sa.Column("how_to_complain_to_dpb", sa.Text, nullable=False),
        sa.UniqueConstraint("notice_id", "locale", name="uq_notice_translation_locale"),
    )

    op.create_table(
        "rights_requests",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("principal_ref", sa.String(255), nullable=False),
        sa.Column("request_type", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="SUBMITTED"),
        sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_rights_tenant_status", "rights_requests", ["tenant_id", "status"])

    op.create_table(
        "grievances",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("principal_ref", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="OPEN"),
        sa.Column("sla_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_grievances_tenant_status", "grievances", ["tenant_id", "status"])

    op.create_table(
        "audit_logs",
        sa.Column("entry_id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("prev_hash", sa.String(64), nullable=False, server_default=""),
        sa.Column("hash_value", sa.String(64), nullable=False),
        sa.Column("payload", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("actor", sa.String(255), nullable=False),
        sa.Column(
            "timestamp", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("retention_until", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_audit_tenant_ts", "audit_logs", ["tenant_id", "timestamp"])

    op.create_table(
        "webhooks",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("secret", sa.String(255), nullable=False),
        sa.Column("events", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", sa.String(20), nullable=False, server_default="ANALYST"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "email", name="uq_user_tenant_email"),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("key_prefix", sa.String(20), nullable=False, unique=True, index=True),
        sa.Column("key_hash", sa.String(255), nullable=False),
        sa.Column("label", sa.String(255), nullable=False),
        sa.Column("allowed_origins", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "consent_receipts",
        sa.Column("receipt_id", sa.String(64), primary_key=True),
        sa.Column(
            "consent_id",
            sa.String(64),
            sa.ForeignKey("consent_artifacts.consent_id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "tenant_id", sa.String(64), sa.ForeignKey("tenants.id"), nullable=False, index=True
        ),
        sa.Column("principal_ref", sa.String(255), nullable=False),
        sa.Column("receipt_data", sa.Text, nullable=False),
        sa.Column(
            "generated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def downgrade() -> None:
    op.drop_table("consent_receipts")
    op.drop_table("api_keys")
    op.drop_table("users")
    op.drop_table("webhooks")
    op.drop_table("audit_logs")
    op.drop_table("grievances")
    op.drop_table("rights_requests")
    op.drop_table("notice_translations")
    op.drop_table("notices")
    op.drop_table("consent_events")
    op.drop_table("consent_artifacts")
    op.drop_table("data_principals")
    op.drop_table("purposes")
    op.drop_table("tenants")
