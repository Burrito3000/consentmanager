"""Service layer — use-case orchestration.

Services depend on repository interfaces (ABCs), not on concrete implementations.
Business logic is in services; API/controllers are thin wrappers.
"""

from src.services.audit_service import AuditService
from src.services.consent_service import ConsentService
from src.services.notice_service import NoticeService
from src.services.rights_service import RightsService
from src.services.webhook_service import WebhookService

__all__ = [
    "AuditService",
    "ConsentService",
    "NoticeService",
    "RightsService",
    "WebhookService",
]
