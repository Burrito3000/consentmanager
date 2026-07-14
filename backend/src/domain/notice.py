"""Notice entity — versioned, multilingual consent notice.

DPDP §5(1): Every consent notice must:
- Be in English + selectable Indian languages
- List itemized data + purpose
- Explain how to withdraw
- Explain how to complain to the DPB (Data Protection Board)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime

from .exceptions import InvalidNoticeError

# ISO 639-1 codes for common Indian languages
INDIAN_LANGUAGES = {
    "en": "English",
    "as": "Assamese",
    "bn": "Bengali",
    "gu": "Gujarati",
    "hi": "Hindi",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "or": "Odia",
    "pa": "Punjabi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
}


@dataclass(frozen=True)
class NoticeTranslation:
    """Translation of a notice into a specific language."""

    locale: str
    title: str
    body_text: str  # DPDP: full description of data collection
    how_to_withdraw: str  # DPDP: clear withdrawal instructions
    how_to_complain_to_dpb: str  # DPDP: DPB complaint procedure

    def __post_init__(self) -> None:
        if not self.locale:
            raise InvalidNoticeError("Locale is required")
        if not self.title:
            raise InvalidNoticeError("Title is required")
        if not self.body_text:
            raise InvalidNoticeError("Body text is required")
        if not self.how_to_withdraw:
            raise InvalidNoticeError("Withdrawal instructions are required")
        if not self.how_to_complain_to_dpb:
            raise InvalidNoticeError("DPB complaint procedure is required")


@dataclass(frozen=True)
class Notice:
    """A versioned consent notice for a specific purpose.

    DPDP §5(1)(a-e): Every notice MUST include:
    - Itemized personal data to be collected
    - Purpose of processing
    - How to withdraw consent
    - How to make a complaint to the Data Protection Board
    - Manner and media in which personal data is to be collected

    Invariants:
    - purpose_id references an active Purpose
    - At least one translation (English minimum)
    - is_published notices cannot be modified (versioned)
    """

    purpose_id: str
    tenant_id: str
    translations: tuple[NoticeTranslation, ...]
    version: int = 1
    is_published: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.purpose_id:
            raise InvalidNoticeError("Purpose ID is required")
        if not self.tenant_id:
            raise InvalidNoticeError("Tenant ID is required")
        if not self.translations:
            raise InvalidNoticeError("At least one translation is required")
        # DPDP: English notice must always be present
        english = any(t.locale == "en" for t in self.translations)
        if not english:
            raise InvalidNoticeError("English (en) translation is required (DPDP §5)")

    def publish(self) -> Notice:
        """Publish this notice. Once published, a new version must be created for edits."""
        return Notice(
            id=self.id,
            purpose_id=self.purpose_id,
            tenant_id=self.tenant_id,
            translations=self.translations,
            version=self.version,
            is_published=True,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )

    def new_version(self, translations: list[NoticeTranslation]) -> Notice:
        """Create a new version of this notice."""
        return Notice(
            purpose_id=self.purpose_id,
            tenant_id=self.tenant_id,
            translations=tuple(translations),
            version=self.version + 1,
            is_published=False,
            created_at=self.created_at,
            updated_at=datetime.now(UTC),
        )

    def get_translation(self, locale: str) -> NoticeTranslation | None:
        for t in self.translations:
            if t.locale == locale:
                return t
        return None
