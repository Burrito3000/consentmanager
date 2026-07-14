"""Webhook service — manage and dispatch webhooks for consent lifecycle events."""

from __future__ import annotations

from typing import Any

from src.domain.exceptions import InvalidWebhookError
from src.domain.webhook import Webhook, WebhookEvent
from src.repositories.interfaces import IWebhookRepository, UnitOfWork
from src.services.audit_service import AuditService


class WebhookService:
    """Service for managing webhook endpoints and dispatching events.

    DPDP: Webhooks fire on withdrawal to notify tenant + downstream processors.
    """

    def __init__(self, uow: UnitOfWork, audit_service: AuditService) -> None:
        self._uow = uow
        self._audit = audit_service

    def register_webhook(
        self,
        tenant_id: str,
        url: str,
        secret: str,
        events: list[WebhookEvent],
    ) -> Webhook:
        """Register a new webhook endpoint for a tenant."""
        webhook = Webhook(
            tenant_id=tenant_id,
            url=url,
            secret=secret,
            events=tuple(events),
        )

        with self._uow:
            repo: IWebhookRepository = self._uow.webhooks
            repo.save(webhook)

            self._audit.log(
                tenant_id=tenant_id,
                action="webhook.registered",
                actor="system",
                payload={
                    "webhook_id": webhook.id,
                    "url": url,
                    "events": [e.value for e in events],
                },
            )
            self._uow.commit()

        return webhook

    def deactivate_webhook(self, webhook_id: str, tenant_id: str) -> Webhook:
        with self._uow:
            repo: IWebhookRepository = self._uow.webhooks
            wh = repo.get_by_id(webhook_id)
            if not wh or wh.tenant_id != tenant_id:
                raise InvalidWebhookError("Webhook not found")

            deactivated = wh.deactivate()
            repo.save(deactivated)

            self._audit.log(
                tenant_id=tenant_id,
                action="webhook.deactivated",
                actor="system",
                payload={"webhook_id": webhook_id},
            )
            self._uow.commit()

        return deactivated

    def list_webhooks(self, tenant_id: str) -> list[Webhook]:
        with self._uow:
            repo: IWebhookRepository = self._uow.webhooks
            return repo.list_by_tenant(tenant_id)

    def dispatch_event(
        self,
        tenant_id: str,
        event: WebhookEvent,
        payload: dict[str, Any],
    ) -> None:
        """Dispatch a webhook event to all subscribed endpoints.

        In production, this is called from Celery tasks (Step 6).
        """
        # TODO: Implement async webhook dispatch via Celery
        pass
