"""Dependency injection container.

Wires services to repositories. The API layer injects via this container.
"""

from __future__ import annotations

from src.infrastructure.database.uow import SqlUnitOfWork
from src.repositories.interfaces import UnitOfWork
from src.services.audit_service import AuditService
from src.services.consent_service import ConsentService
from src.services.notice_service import NoticeService
from src.services.rights_service import RightsService
from src.services.webhook_service import WebhookService


class ServiceContainer:
    """Simple DI container for services.

    Usage:
        container = ServiceContainer()
        consent_service = container.consent_service()
    """

    def __init__(self, uow: UnitOfWork | None = None) -> None:
        self._uow = uow
        self._audit_service: AuditService | None = None
        self._consent_service: ConsentService | None = None
        self._rights_service: RightsService | None = None
        self._notice_service: NoticeService | None = None
        self._webhook_service: WebhookService | None = None

    def get_uow(self) -> UnitOfWork:
        if self._uow is None:
            self._uow = SqlUnitOfWork()
        return self._uow

    def audit_service(self) -> AuditService:
        if self._audit_service is None:
            self._audit_service = AuditService(uow=self.get_uow())
        return self._audit_service

    def consent_service(self) -> ConsentService:
        if self._consent_service is None:
            self._consent_service = ConsentService(
                uow=self.get_uow(),
                audit_service=self.audit_service(),
            )
        return self._consent_service

    def rights_service(self) -> RightsService:
        if self._rights_service is None:
            self._rights_service = RightsService(
                uow=self.get_uow(),
                audit_service=self.audit_service(),
            )
        return self._rights_service

    def notice_service(self) -> NoticeService:
        if self._notice_service is None:
            self._notice_service = NoticeService(
                uow=self.get_uow(),
                audit_service=self.audit_service(),
            )
        return self._notice_service

    def webhook_service(self) -> WebhookService:
        if self._webhook_service is None:
            self._webhook_service = WebhookService(
                uow=self.get_uow(),
                audit_service=self.audit_service(),
            )
        return self._webhook_service
