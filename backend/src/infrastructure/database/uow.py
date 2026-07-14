"""SQLAlchemy Unit of Work implementation."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.infrastructure.database.repositories import (
    SqlApiKeyRepository,
    SqlAuditLogRepository,
    SqlConsentEventRepository,
    SqlConsentReceiptRepository,
    SqlConsentRepository,
    SqlDataPrincipalRepository,
    SqlGrievanceRepository,
    SqlNoticeRepository,
    SqlPurposeRepository,
    SqlRightsRequestRepository,
    SqlTenantRepository,
    SqlUserRepository,
    SqlWebhookRepository,
)
from src.infrastructure.database.session import SessionLocal
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
    UnitOfWork,
)


class SqlUnitOfWork(UnitOfWork):
    """Unit of Work backed by SQLAlchemy sessions.

    Usage:
        uow = SqlUnitOfWork()
        with uow:
            uow.tenants.save(tenant)
            uow.commit()
    """

    def __init__(self, session: Session | None = None) -> None:
        self._session = session or SessionLocal()
        self._tenants: SqlTenantRepository | None = None
        self._purposes: SqlPurposeRepository | None = None
        self._principals: SqlDataPrincipalRepository | None = None
        self._consents: SqlConsentRepository | None = None
        self._consent_events: SqlConsentEventRepository | None = None
        self._notices: SqlNoticeRepository | None = None
        self._rights_requests: SqlRightsRequestRepository | None = None
        self._grievances: SqlGrievanceRepository | None = None
        self._audit_logs: SqlAuditLogRepository | None = None
        self._webhooks: SqlWebhookRepository | None = None
        self._users: SqlUserRepository | None = None
        self._api_keys: SqlApiKeyRepository | None = None
        self._receipts: SqlConsentReceiptRepository | None = None

    def __enter__(self) -> SqlUnitOfWork:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is not None:
            self.rollback()
        self._session.close()

    def flush(self) -> None:
        self._session.flush()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    @property
    def tenants(self) -> ITenantRepository:
        if self._tenants is None:
            self._tenants = SqlTenantRepository(self._session)
        return self._tenants

    @property
    def purposes(self) -> IPurposeRepository:
        if self._purposes is None:
            self._purposes = SqlPurposeRepository(self._session)
        return self._purposes

    @property
    def principals(self) -> IDataPrincipalRepository:
        if self._principals is None:
            self._principals = SqlDataPrincipalRepository(self._session)
        return self._principals

    @property
    def consents(self) -> IConsentRepository:
        if self._consents is None:
            self._consents = SqlConsentRepository(self._session)
        return self._consents

    @property
    def consent_events(self) -> IConsentEventRepository:
        if self._consent_events is None:
            self._consent_events = SqlConsentEventRepository(self._session)
        return self._consent_events

    @property
    def notices(self) -> INoticeRepository:
        if self._notices is None:
            self._notices = SqlNoticeRepository(self._session)
        return self._notices

    @property
    def rights_requests(self) -> IRightsRequestRepository:
        if self._rights_requests is None:
            self._rights_requests = SqlRightsRequestRepository(self._session)
        return self._rights_requests

    @property
    def grievances(self) -> IGrievanceRepository:
        if self._grievances is None:
            self._grievances = SqlGrievanceRepository(self._session)
        return self._grievances

    @property
    def audit_logs(self) -> IAuditLogRepository:
        if self._audit_logs is None:
            self._audit_logs = SqlAuditLogRepository(self._session)
        return self._audit_logs

    @property
    def webhooks(self) -> IWebhookRepository:
        if self._webhooks is None:
            self._webhooks = SqlWebhookRepository(self._session)
        return self._webhooks

    @property
    def users(self) -> IUserRepository:
        if self._users is None:
            self._users = SqlUserRepository(self._session)
        return self._users

    @property
    def api_keys(self) -> IApiKeyRepository:
        if self._api_keys is None:
            self._api_keys = SqlApiKeyRepository(self._session)
        return self._api_keys

    @property
    def consent_receipts(self) -> IConsentReceiptRepository:
        if self._receipts is None:
            self._receipts = SqlConsentReceiptRepository(self._session)
        return self._receipts
