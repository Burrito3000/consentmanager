"""Domain-specific exceptions. All inherit from a common base."""


class DomainError(Exception):
    """Base for all domain errors."""


class InvalidTenantError(DomainError):
    """Raised when tenant data violates invariants."""


class InvalidPurposeError(DomainError):
    """Raised when purpose data violates DPDP rules."""


class InvalidConsentError(DomainError):
    """Raised when consent operation violates DPDP rules."""


class InvalidNoticeError(DomainError):
    """Raised when notice content violates DPDP rules."""


class InvalidRightsRequestError(DomainError):
    """Raised when rights request violates DPDP rules."""


class InvalidAuditChainError(DomainError):
    """Raised when audit chain verification fails."""


class DataPrincipalNotFoundError(DomainError):
    """Raised when a data principal is not found."""


class PurposeNotFoundError(DomainError):
    """Raised when a purpose is not found."""


class ConsentNotFoundError(DomainError):
    """Raised when consent artifact is not found."""


class ConsentExpiredError(DomainError):
    """Raised when trying to modify an expired consent."""


class WithdrawalNotAllowedError(DomainError):
    """Raised when withdrawal is not allowed for a consent."""


class BundledConsentError(InvalidConsentError):
    """Raised when multiple purposes are bundled without per-purpose choice."""


class UnauthorizedActionError(DomainError):
    """Raised when an actor lacks permission."""


class InvalidWebhookError(DomainError):
    """Raised when webhook config is invalid."""


class SLABreachError(DomainError):
    """Raised when SLA deadline has passed."""
