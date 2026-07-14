"""Tests for the Webhook domain entity."""

import pytest

from src.domain.exceptions import InvalidWebhookError
from src.domain.webhook import Webhook, WebhookEvent


class TestWebhook:
    def test_create_valid_webhook(self) -> None:
        wh = Webhook(
            tenant_id="t1",
            url="https://hooks.acme.com/consent",
            secret="whsec_abc123",
            events=(WebhookEvent.CONSENT_GRANTED, WebhookEvent.CONSENT_WITHDRAWN),
        )
        assert wh.url == "https://hooks.acme.com/consent"
        assert wh.is_active is True
        assert len(wh.events) == 2

    def test_webhook_without_https_raises_error(self) -> None:
        with pytest.raises(InvalidWebhookError, match="HTTPS"):
            Webhook(
                tenant_id="t1",
                url="http://hooks.acme.com/consent",
                secret="whsec_abc",
                events=(WebhookEvent.CONSENT_GRANTED,),
            )

    def test_webhook_without_secret_raises_error(self) -> None:
        with pytest.raises(InvalidWebhookError, match="secret"):
            Webhook(
                tenant_id="t1",
                url="https://hooks.acme.com/consent",
                secret="",
                events=(WebhookEvent.CONSENT_GRANTED,),
            )

    def test_webhook_without_events_raises_error(self) -> None:
        with pytest.raises(InvalidWebhookError, match="event"):
            Webhook(
                tenant_id="t1",
                url="https://hooks.acme.com/consent",
                secret="whsec_abc",
                events=(),
            )

    def test_subscribes_to_event(self) -> None:
        wh = Webhook(
            tenant_id="t1",
            url="https://hooks.acme.com/consent",
            secret="whsec_abc",
            events=(WebhookEvent.CONSENT_GRANTED,),
        )
        assert wh.subscribes_to(WebhookEvent.CONSENT_GRANTED) is True
        assert wh.subscribes_to(WebhookEvent.CONSENT_WITHDRAWN) is False

    def test_deactivate_webhook(self) -> None:
        wh = Webhook(
            tenant_id="t1",
            url="https://hooks.acme.com/consent",
            secret="whsec_abc",
            events=(WebhookEvent.CONSENT_GRANTED,),
        )
        deactivated = wh.deactivate()
        assert deactivated.is_active is False
        assert deactivated.id == wh.id
