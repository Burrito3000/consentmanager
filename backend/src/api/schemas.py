"""Pydantic v2 schemas for the public API."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ── Consent Schemas ──────────────────────────────────────────────────────────


class PurposeGrantRequest(BaseModel):
    purpose_id: str
    granted: bool = True
    data_categories: list[str] = Field(default_factory=list)


class ConsentGrantRequest(BaseModel):
    principal_ref: str
    purpose_grants: list[PurposeGrantRequest] = Field(min_length=1)
    notice_version: str
    expires_at: datetime | None = None
    ip_address: str | None = None
    user_agent: str | None = None

    @field_validator("purpose_grants")
    @classmethod
    def check_at_least_one_granted(cls, v: list[PurposeGrantRequest]) -> list[PurposeGrantRequest]:
        if not any(pg.granted for pg in v):
            raise ValueError("At least one purpose must be granted")
        return v


class ConsentModifyRequest(BaseModel):
    principal_ref: str
    purpose_grants: list[PurposeGrantRequest] = Field(min_length=1)
    notice_version: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None


class ConsentWithdrawRequest(BaseModel):
    principal_ref: str
    ip_address: str | None = None
    user_agent: str | None = None


class ConsentResponse(BaseModel):
    consent_id: str
    status: str
    principal_ref: str
    purpose_consents: list[dict[str, Any]]
    created_at: datetime
    modified_at: datetime
    expires_at: datetime | None = None


class ConsentEventResponse(BaseModel):
    event_id: str
    event_type: str
    timestamp: datetime
    purpose_consents: list[dict[str, Any]]
    ip_address: str | None = None
    notice_version: str | None = None


class ConsentDetailResponse(BaseModel):
    artifact: ConsentResponse
    current_status: str
    events: list[ConsentEventResponse]


class ConsentGrantResponse(BaseModel):
    consent_id: str
    status: str
    receipt: str


# ── Rights Request Schemas ───────────────────────────────────────────────────


class RightsRequestCreate(BaseModel):
    principal_ref: str
    request_type: str
    notes: str | None = None

    @field_validator("request_type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        allowed = {"ACCESS", "CORRECTION", "ERASURE", "GRIEVANCE", "NOMINEE", "WITHDRAW"}
        if v.upper() not in allowed:
            raise ValueError(f"Invalid request type. Must be one of: {allowed}")
        return v.upper()


class RightsRequestResponse(BaseModel):
    id: str
    request_type: str
    status: str
    sla_due_at: datetime | None = None
    submitted_at: datetime
    resolved_at: datetime | None = None


# ── Grievance Schemas ────────────────────────────────────────────────────────


class GrievanceCreate(BaseModel):
    principal_ref: str
    subject: str
    description: str


class GrievanceResponse(BaseModel):
    id: str
    subject: str
    status: str
    sla_due_at: datetime | None = None
    submitted_at: datetime
    resolved_at: datetime | None = None


# ── Notice Schemas ───────────────────────────────────────────────────────────


class NoticeTranslationSchema(BaseModel):
    locale: str
    title: str
    body_text: str
    how_to_withdraw: str
    how_to_complain_to_dpb: str


class NoticeCreateRequest(BaseModel):
    purpose_id: str
    translations: list[NoticeTranslationSchema] = Field(min_length=1)


class NoticeVersionRequest(BaseModel):
    translations: list[NoticeTranslationSchema] = Field(min_length=1)


class NoticeResponse(BaseModel):
    id: str
    purpose_id: str
    version: int
    is_published: bool
    translations: list[NoticeTranslationSchema]
    created_at: datetime


# ── Webhook Schemas ──────────────────────────────────────────────────────────


class WebhookCreateRequest(BaseModel):
    url: str
    secret: str
    events: list[str] = Field(min_length=1)


class WebhookResponse(BaseModel):
    id: str
    url: str
    events: list[str]
    is_active: bool
    created_at: datetime


# ── Error Schema ─────────────────────────────────────────────────────────────


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


# ── Health ────────────────────────────────────────────────────────────────────


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
