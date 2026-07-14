"""Notice service — versioned, multilingual consent notices."""

from __future__ import annotations

from src.domain.exceptions import InvalidNoticeError
from src.domain.notice import INDIAN_LANGUAGES, Notice, NoticeTranslation
from src.repositories.interfaces import INoticeRepository, IPurposeRepository, UnitOfWork
from src.services.audit_service import AuditService


class NoticeService:
    """Service for creating and managing multilingual consent notices.

    DPDP §5: Every notice must support English + Indian languages,
    list itemized data + purpose, explain withdrawal and DPB complaint process.
    """

    def __init__(self, uow: UnitOfWork, audit_service: AuditService) -> None:
        self._uow = uow
        self._audit = audit_service

    def create_notice(
        self,
        purpose_id: str,
        tenant_id: str,
        translations: list[dict[str, str]],
    ) -> Notice:
        """Create a new consent notice for a purpose."""
        with self._uow:
            purpose_repo: IPurposeRepository = self._uow.purposes
            purpose = purpose_repo.get_by_id(purpose_id)
            if not purpose or purpose.tenant_id != tenant_id:
                raise InvalidNoticeError("Purpose not found")

            notice_translations = [
                NoticeTranslation(
                    locale=t["locale"],
                    title=t["title"],
                    body_text=t["body_text"],
                    how_to_withdraw=t["how_to_withdraw"],
                    how_to_complain_to_dpb=t["how_to_complain_to_dpb"],
                )
                for t in translations
            ]

            notice = Notice(
                purpose_id=purpose_id,
                tenant_id=tenant_id,
                translations=tuple(notice_translations),
            )

            repo: INoticeRepository = self._uow.notices
            repo.save(notice)

            self._audit.log(
                tenant_id=tenant_id,
                action="notice.created",
                actor="system",
                payload={
                    "notice_id": notice.id,
                    "purpose_id": purpose_id,
                    "version": notice.version,
                    "locales": [t.locale for t in notice_translations],
                },
            )
            self._uow.commit()

        return notice

    def publish_notice(self, notice_id: str, tenant_id: str) -> Notice:
        """Publish a notice. Once published, edits require a new version."""
        with self._uow:
            repo: INoticeRepository = self._uow.notices
            notice = repo.get_by_id(notice_id)
            if not notice or notice.tenant_id != tenant_id:
                raise InvalidNoticeError("Notice not found")

            published = notice.publish()
            repo.save(published)

            self._audit.log(
                tenant_id=tenant_id,
                action="notice.published",
                actor="system",
                payload={"notice_id": notice_id, "version": published.version},
            )
            self._uow.commit()

        return published

    def create_new_version(
        self,
        notice_id: str,
        tenant_id: str,
        translations: list[dict[str, str]],
    ) -> Notice:
        """Create a new version of an existing notice."""
        with self._uow:
            repo: INoticeRepository = self._uow.notices
            existing = repo.get_by_id(notice_id)
            if not existing or existing.tenant_id != tenant_id:
                raise InvalidNoticeError("Notice not found")

            notice_translations = [
                NoticeTranslation(
                    locale=t["locale"],
                    title=t["title"],
                    body_text=t["body_text"],
                    how_to_withdraw=t["how_to_withdraw"],
                    how_to_complain_to_dpb=t["how_to_complain_to_dpb"],
                )
                for t in translations
            ]

            new_version = existing.new_version(notice_translations)
            repo.save(new_version)

            self._audit.log(
                tenant_id=tenant_id,
                action="notice.versioned",
                actor="system",
                payload={
                    "notice_id": new_version.id,
                    "previous_version": existing.version,
                    "new_version": new_version.version,
                },
            )
            self._uow.commit()

        return new_version

    def get_published_notice(self, purpose_id: str) -> Notice | None:
        with self._uow:
            repo: INoticeRepository = self._uow.notices
            return repo.get_published_by_purpose(purpose_id)

    def list_supported_languages(self) -> dict[str, str]:
        return dict(INDIAN_LANGUAGES)
