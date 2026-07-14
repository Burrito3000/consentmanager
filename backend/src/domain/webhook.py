"""Webhook entity — outbound notifications for consent lifecycle events.

DPDP: Withdrawal must fire webhooks to tenant + downstream processors.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from .exceptions import InvalidWebhookError


class WebhookEvent(StrEnum):
    CONSENT_GRANTED = "consent.granted"
    CONSENT_MODIFIED = "consent.modified"
    CONSENT_WITHDRAWN = "consent.withdrawn"
    CONSENT_EXPIRED = "consent.expired"
    RIGHTS_REQUEST_SUBMITTED = "rights_request.submitted"
    RIGHTS_REQUEST_RESOLVED = "rights_request.resolved"
    GRIEVANCE_SUBMITTED = "grievance.submitted"
    GRIEVANCE_RESOLVED = "grievance.resolved"


@dataclass(frozen=True)
class Webhook:
    """An outbound webhook configuration for a tenant.

    Invariants:
    - url must be a valid HTTPS URL
    - at least one event must be subscribed
    - secret is required for HMAC signing
    """

    tenant_id: str
    url: str
    secret: str
    events: tuple[WebhookEvent, ...]
    is_active: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.url:
            raise InvalidWebhookError("URL is required")
        if not self.url.startswith("https://"):
            raise InvalidWebhookError("Webhook URL must use HTTPS")
        if not self.secret:
            raise InvalidWebhookError("Webhook secret is required")
        if not self.events:
            raise InvalidWebhookError("At least one event must be subscribed")
        if not self.tenant_id:
            raise InvalidWebhookError("Tenant ID is required")

    def subscribes_to(self, event: WebhookEvent) -> bool:
        return event in self.events

    def deactivate(self) -> Webhook:
        return Webhook(
            id=self.id,
            tenant_id=self.tenant_id,
            url=self.url,
            secret=self.secret,
            events=self.events,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )
