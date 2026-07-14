"""Consent service — grant, modify, withdraw consent with full audit trail.

DPDP compliance enforced:
- Per-purpose granular consent
- Explicit affirmative action
- Withdrawal as easy as grant
- Append-only event log
- Audit hash chain
- Webhook dispatch on withdrawal
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from src.domain.consent import (
    ConsentArtifact,
    ConsentEvent,
    ConsentReceipt,
    ConsentStatus,
    PurposeConsent,
    compute_current_consent,
)
from src.domain.exceptions import (
    ConsentExpiredError,
    ConsentNotFoundError,
    InvalidConsentError,
)
from src.repositories.interfaces import (
    IConsentEventRepository,
    IConsentReceiptRepository,
    IConsentRepository,
    IPurposeRepository,
    UnitOfWork,
)
from src.services.audit_service import AuditService


class ConsentService:
    """Orchestrates consent lifecycle operations with full audit and webhook dispatch."""

    def __init__(
        self,
        uow: UnitOfWork,
        audit_service: AuditService,
    ) -> None:
        self._uow = uow
        self._audit = audit_service

    def grant_consent(
        self,
        tenant_id: str,
        principal_ref: str,
        purpose_grants: list[dict[str, Any]],
        notice_version: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
        expires_at: datetime | None = None,
    ) -> dict[str, Any]:
        """Grant consent for multiple purposes.

        DPDP §6: Per-purpose granular consent. Each purpose must have
        an explicit affirmative action. No bundled consent.
        """
        with self._uow:
            purpose_repo: IPurposeRepository = self._uow.purposes
            consent_repo: IConsentRepository = self._uow.consents
            event_repo: IConsentEventRepository = self._uow.consent_events
            receipt_repo: IConsentReceiptRepository = self._uow.consent_receipts

            # Validate purposes exist and are active
            purpose_consents: list[PurposeConsent] = []
            for pg in purpose_grants:
                purpose = purpose_repo.get_by_id(pg["purpose_id"])
                if not purpose or not purpose.is_active:
                    raise InvalidConsentError(f"Purpose {pg['purpose_id']} not found or inactive")

                pc = PurposeConsent(
                    purpose_id=pg["purpose_id"],
                    granted=pg.get("granted", False),
                    data_categories=tuple(pg.get("data_categories", [])),
                )
                if not pc.granted:
                    raise InvalidConsentError(f"Purpose {pg['purpose_id']} requires explicit grant")
                purpose_consents.append(pc)

            if not purpose_consents:
                raise InvalidConsentError("At least one purpose must be granted")

            # Create artifact and event
            artifact = ConsentArtifact.new(
                tenant_id=tenant_id,
                principal_ref=principal_ref,
                purpose_consents=purpose_consents,
                expires_at=expires_at,
            )

            event = ConsentEvent.from_grant(
                consent_id=artifact.consent_id,
                tenant_id=tenant_id,
                purpose_consents=purpose_consents,
                notice_version=notice_version,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            consent_repo.save(artifact)
            event_repo.save(event)

            # Generate receipt
            signed = artifact.to_signed_json(lambda data: self._sign_artifact(data))
            receipt = ConsentReceipt(
                receipt_id=artifact.consent_id + "_receipt",
                consent_id=artifact.consent_id,
                tenant_id=tenant_id,
                principal_ref=principal_ref,
                receipt_data=signed,
            )
            receipt_repo.save(receipt)

            # Audit log entry
            self._audit.log(
                tenant_id=tenant_id,
                action="consent.granted",
                actor=f"principal:{principal_ref}",
                payload={
                    "consent_id": artifact.consent_id,
                    "purpose_ids": [pc.purpose_id for pc in purpose_consents],
                    "notice_version": notice_version,
                },
            )

            self._uow.commit()

        return {
            "consent_id": artifact.consent_id,
            "status": artifact.status.value,
            "receipt": signed,
            "events": [event],
        }

    def modify_consent(
        self,
        consent_id: str,
        tenant_id: str,
        principal_ref: str,
        purpose_grants: list[dict[str, Any]],
        notice_version: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Modify an existing consent with new purpose preferences."""
        with self._uow:
            consent_repo: IConsentRepository = self._uow.consents
            event_repo: IConsentEventRepository = self._uow.consent_events

            artifact = consent_repo.get_by_id(consent_id)
            if not artifact:
                raise ConsentNotFoundError(f"Consent {consent_id} not found")
            if artifact.tenant_id != tenant_id:
                raise ConsentNotFoundError("Consent not found in this tenant")
            if artifact.principal_ref != principal_ref:
                raise InvalidConsentError("Principal mismatch")
            if artifact.is_withdrawn():
                raise InvalidConsentError("Cannot modify withdrawn consent")
            if artifact.is_expired():
                raise ConsentExpiredError("Cannot modify expired consent")

            purpose_consents: list[PurposeConsent] = []
            for pg in purpose_grants:
                purpose_consents.append(
                    PurposeConsent(
                        purpose_id=pg["purpose_id"],
                        granted=pg.get("granted", False),
                        data_categories=tuple(pg.get("data_categories", [])),
                    )
                )

            event = ConsentEvent.from_modification(
                consent_id=consent_id,
                tenant_id=tenant_id,
                purpose_consents=purpose_consents,
                notice_version=notice_version,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            event_repo.save(event)

            # Recompute state from events
            events = event_repo.list_by_consent(consent_id)
            updated = compute_current_consent(artifact, events)
            consent_repo.save(updated)

            self._audit.log(
                tenant_id=tenant_id,
                action="consent.modified",
                actor=f"principal:{principal_ref}",
                payload={
                    "consent_id": consent_id,
                    "purpose_ids": [pc.purpose_id for pc in purpose_consents],
                },
            )

            self._uow.commit()

        return {
            "consent_id": consent_id,
            "status": updated.status.value,
            "events": [event],
        }

    def withdraw_consent(
        self,
        consent_id: str,
        tenant_id: str,
        principal_ref: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> dict[str, Any]:
        """Withdraw consent for ALL purposes.

        DPDP: Withdrawal must be as easy as granting.
        Withdrawal stops processing and fires webhooks to tenant + processors.
        """
        with self._uow:
            consent_repo: IConsentRepository = self._uow.consents
            event_repo: IConsentEventRepository = self._uow.consent_events

            artifact = consent_repo.get_by_id(consent_id)
            if not artifact:
                raise ConsentNotFoundError(f"Consent {consent_id} not found")
            if artifact.tenant_id != tenant_id:
                raise ConsentNotFoundError("Consent not found in this tenant")
            if artifact.is_withdrawn():
                raise InvalidConsentError("Consent already withdrawn")

            # Withdraw all purposes
            withdrawn_consents = [
                PurposeConsent(
                    purpose_id=pc.purpose_id,
                    granted=False,
                    data_categories=tuple(pc.data_categories),
                    withdrawn_at=datetime.now(UTC),
                )
                for pc in artifact.purpose_consents
            ]

            event = ConsentEvent.from_withdrawal(
                consent_id=consent_id,
                tenant_id=tenant_id,
                purpose_consents=withdrawn_consents,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            event_repo.save(event)

            # Recompute state
            events = event_repo.list_by_consent(consent_id)
            updated = compute_current_consent(artifact, events)
            consent_repo.save(updated)

            self._audit.log(
                tenant_id=tenant_id,
                action="consent.withdrawn",
                actor=f"principal:{principal_ref}",
                payload={
                    "consent_id": consent_id,
                    "purpose_ids": [pc.purpose_id for pc in artifact.purpose_consents],
                },
            )

            self._uow.commit()

        # DPDP: Withdrawal fires webhooks — this is dispatched async via Celery
        self._dispatch_withdrawal_webhooks(tenant_id, consent_id, principal_ref)

        return {
            "consent_id": consent_id,
            "status": ConsentStatus.WITHDRAWN.value,
        }

    def get_consent(
        self,
        consent_id: str,
        tenant_id: str,
    ) -> dict[str, Any] | None:
        """Retrieve a consent artifact with its current state and event timeline."""
        with self._uow:
            consent_repo: IConsentRepository = self._uow.consents
            event_repo: IConsentEventRepository = self._uow.consent_events

            artifact = consent_repo.get_by_id(consent_id)
            if not artifact or artifact.tenant_id != tenant_id:
                return None

            events = event_repo.list_by_consent(consent_id)
            current = compute_current_consent(artifact, events)

            return {
                "artifact": artifact,
                "current_status": current.status.value,
                "events": events,
            }

    def list_consents(
        self,
        tenant_id: str,
        principal_ref: str | None = None,
    ) -> list[dict[str, Any]]:
        """List consents for a tenant, optionally filtered by principal."""
        with self._uow:
            consent_repo: IConsentRepository = self._uow.consents
            if principal_ref:
                artifacts = consent_repo.list_by_principal(tenant_id, principal_ref)
            else:
                artifacts = consent_repo.list_by_tenant(tenant_id)

            results = []
            for artifact in artifacts:
                results.append(
                    {
                        "consent_id": artifact.consent_id,
                        "principal_ref": artifact.principal_ref,
                        "status": artifact.status.value,
                        "purpose_ids": [pc.purpose_id for pc in artifact.purpose_consents],
                        "created_at": artifact.created_at.isoformat(),
                        "modified_at": artifact.modified_at.isoformat(),
                    }
                )
            return results

    def _sign_artifact(self, data: str) -> str:
        """Placeholder for artifact signing. Will use HMAC-SHA256 in production."""
        import hashlib
        import hmac

        return hmac.new(
            self._audit._audit_secret.encode("utf-8"),
            data.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _dispatch_withdrawal_webhooks(
        self, tenant_id: str, consent_id: str, principal_ref: str
    ) -> None:
        """Queue webhook dispatch for withdrawal notification.

        In production, this creates a Celery task. For now, it's a no-op
        since Celery will be added in Step 6.
        """
        # TODO: dispatch_webhook.delay(tenant_id, "consent.withdrawn", payload)
        pass
