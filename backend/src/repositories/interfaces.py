"""Abstract repository interfaces (ABCs) for the domain.

Dependencies point inward: service layer depends on these interfaces,
not on concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.api_key import ApiKey
from src.domain.audit import AuditLogEntry
from src.domain.consent import ConsentArtifact, ConsentEvent, ConsentReceipt
from src.domain.notice import Notice
from src.domain.principal import DataPrincipal
from src.domain.purpose import Purpose
from src.domain.rights import Grievance, RightsRequest
from src.domain.tenant import Tenant
from src.domain.user import User
from src.domain.webhook import Webhook


class ITenantRepository(ABC):
    @abstractmethod
    def save(self, tenant: Tenant) -> Tenant: ...

    @abstractmethod
    def get_by_id(self, tenant_id: str) -> Tenant | None: ...

    @abstractmethod
    def list_all(self) -> list[Tenant]: ...


class IPurposeRepository(ABC):
    @abstractmethod
    def save(self, purpose: Purpose) -> Purpose: ...

    @abstractmethod
    def get_by_id(self, purpose_id: str) -> Purpose | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[Purpose]: ...

    @abstractmethod
    def list_active_by_tenant(self, tenant_id: str) -> list[Purpose]: ...


class IDataPrincipalRepository(ABC):
    @abstractmethod
    def save(self, principal: DataPrincipal) -> DataPrincipal: ...

    @abstractmethod
    def get_by_id(self, principal_id: str) -> DataPrincipal | None: ...

    @abstractmethod
    def get_by_external_ref(self, tenant_id: str, external_ref: str) -> DataPrincipal | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[DataPrincipal]: ...


class IConsentRepository(ABC):
    @abstractmethod
    def save(self, artifact: ConsentArtifact) -> ConsentArtifact: ...

    @abstractmethod
    def get_by_id(self, consent_id: str) -> ConsentArtifact | None: ...

    @abstractmethod
    def list_by_principal(self, tenant_id: str, principal_ref: str) -> list[ConsentArtifact]: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[ConsentArtifact]: ...

    @abstractmethod
    def list_active_by_tenant(self, tenant_id: str) -> list[ConsentArtifact]: ...


class IConsentEventRepository(ABC):
    @abstractmethod
    def save(self, event: ConsentEvent) -> ConsentEvent: ...

    @abstractmethod
    def list_by_consent(self, consent_id: str) -> list[ConsentEvent]: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[ConsentEvent]: ...


class INoticeRepository(ABC):
    @abstractmethod
    def save(self, notice: Notice) -> Notice: ...

    @abstractmethod
    def get_by_id(self, notice_id: str) -> Notice | None: ...

    @abstractmethod
    def list_by_purpose(self, purpose_id: str) -> list[Notice]: ...

    @abstractmethod
    def get_latest_by_purpose(self, purpose_id: str) -> Notice | None: ...

    @abstractmethod
    def get_published_by_purpose(self, purpose_id: str) -> Notice | None: ...


class IRightsRequestRepository(ABC):
    @abstractmethod
    def save(self, request: RightsRequest) -> RightsRequest: ...

    @abstractmethod
    def get_by_id(self, request_id: str) -> RightsRequest | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[RightsRequest]: ...

    @abstractmethod
    def list_by_principal(self, tenant_id: str, principal_ref: str) -> list[RightsRequest]: ...

    @abstractmethod
    def list_pending(self, tenant_id: str) -> list[RightsRequest]: ...


class IGrievanceRepository(ABC):
    @abstractmethod
    def save(self, grievance: Grievance) -> Grievance: ...

    @abstractmethod
    def get_by_id(self, grievance_id: str) -> Grievance | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[Grievance]: ...

    @abstractmethod
    def list_open(self, tenant_id: str) -> list[Grievance]: ...


class IAuditLogRepository(ABC):
    @abstractmethod
    def save(self, entry: AuditLogEntry) -> AuditLogEntry: ...

    @abstractmethod
    def get_by_id(self, entry_id: str) -> AuditLogEntry | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[AuditLogEntry]: ...

    @abstractmethod
    def get_latest(self, tenant_id: str) -> AuditLogEntry | None: ...

    @abstractmethod
    def verify_chain(self, tenant_id: str) -> bool: ...


class IWebhookRepository(ABC):
    @abstractmethod
    def save(self, webhook: Webhook) -> Webhook: ...

    @abstractmethod
    def get_by_id(self, webhook_id: str) -> Webhook | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[Webhook]: ...

    @abstractmethod
    def list_active_by_tenant(self, tenant_id: str) -> list[Webhook]: ...


class IUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User: ...

    @abstractmethod
    def get_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    def get_by_email(self, tenant_id: str, email: str) -> User | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[User]: ...


class IApiKeyRepository(ABC):
    @abstractmethod
    def save(self, api_key: ApiKey) -> ApiKey: ...

    @abstractmethod
    def get_by_id(self, key_id: str) -> ApiKey | None: ...

    @abstractmethod
    def get_by_prefix(self, key_prefix: str) -> ApiKey | None: ...

    @abstractmethod
    def list_by_tenant(self, tenant_id: str) -> list[ApiKey]: ...


class IConsentReceiptRepository(ABC):
    @abstractmethod
    def save(self, receipt: ConsentReceipt) -> ConsentReceipt: ...

    @abstractmethod
    def get_by_id(self, receipt_id: str) -> ConsentReceipt | None: ...

    @abstractmethod
    def get_by_consent(self, consent_id: str) -> ConsentReceipt | None: ...


class UnitOfWork(ABC):
    """Unit of Work pattern for transactional consistency."""

    @abstractmethod
    def __enter__(self): ...

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    def flush(self): ...

    @abstractmethod
    def commit(self): ...

    @abstractmethod
    def rollback(self): ...

    @property
    @abstractmethod
    def tenants(self) -> ITenantRepository: ...

    @property
    @abstractmethod
    def purposes(self) -> IPurposeRepository: ...

    @property
    @abstractmethod
    def principals(self) -> IDataPrincipalRepository: ...

    @property
    @abstractmethod
    def consents(self) -> IConsentRepository: ...

    @property
    @abstractmethod
    def consent_events(self) -> IConsentEventRepository: ...

    @property
    @abstractmethod
    def notices(self) -> INoticeRepository: ...

    @property
    @abstractmethod
    def rights_requests(self) -> IRightsRequestRepository: ...

    @property
    @abstractmethod
    def grievances(self) -> IGrievanceRepository: ...

    @property
    @abstractmethod
    def audit_logs(self) -> IAuditLogRepository: ...

    @property
    @abstractmethod
    def webhooks(self) -> IWebhookRepository: ...

    @property
    @abstractmethod
    def users(self) -> IUserRepository: ...

    @property
    @abstractmethod
    def api_keys(self) -> IApiKeyRepository: ...

    @property
    @abstractmethod
    def consent_receipts(self) -> IConsentReceiptRepository: ...
