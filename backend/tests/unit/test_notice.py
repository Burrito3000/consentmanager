"""Tests for the Notice domain entity — DPDP multilingual consent notices."""

import pytest

from src.domain.exceptions import InvalidNoticeError
from src.domain.notice import INDIAN_LANGUAGES, Notice, NoticeTranslation


class TestNoticeTranslation:
    def test_create_valid_translation(self) -> None:
        t = NoticeTranslation(
            locale="hi",
            title="सहमति सूचना",
            body_text="हम आपकी जानकारी एकत्र करते हैं",
            how_to_withdraw="सहमति वापस लेने के लिए यहाँ क्लिक करें",
            how_to_complain_to_dpb="शिकायत दर्ज करने के लिए डीपीबी से संपर्क करें",
        )
        assert t.locale == "hi"

    def test_translation_missing_fields_raises_error(self) -> None:
        with pytest.raises(InvalidNoticeError, match="Title"):
            NoticeTranslation(
                locale="hi",
                title="",
                body_text="Test",
                how_to_withdraw="Test",
                how_to_complain_to_dpb="Test",
            )


class TestNotice:
    def test_create_valid_notice(self) -> None:
        notice = Notice(
            purpose_id="p1",
            tenant_id="t1",
            translations=(
                NoticeTranslation(
                    locale="en",
                    title="Consent Notice",
                    body_text="We collect your data for processing",
                    how_to_withdraw="Click here to withdraw",
                    how_to_complain_to_dpb="Contact DPB at complaints@dpb.gov.in",
                ),
                NoticeTranslation(
                    locale="hi",
                    title="सहमति सूचना",
                    body_text="हम प्रसंस्करण के लिए आपका डेटा एकत्र करते हैं",
                    how_to_withdraw="सहमति वापस लेने के लिए यहाँ क्लिक करें",
                    how_to_complain_to_dpb="शिकायत के लिए डीपीबी से संपर्क करें",
                ),
            ),
        )
        assert notice.version == 1
        assert len(notice.translations) == 2
        assert notice.is_published is False

    def test_notice_without_english_raises_error(self) -> None:
        """DPDP: English notice must always be present."""
        with pytest.raises(InvalidNoticeError, match="English"):
            Notice(
                purpose_id="p1",
                tenant_id="t1",
                translations=(
                    NoticeTranslation(
                        locale="hi",
                        title="सहमति सूचना",
                        body_text="Test",
                        how_to_withdraw="Test",
                        how_to_complain_to_dpb="Test",
                    ),
                ),
            )

    def test_notice_without_translations_raises_error(self) -> None:
        with pytest.raises(InvalidNoticeError, match="translation"):
            Notice(
                purpose_id="p1",
                tenant_id="t1",
                translations=(),
            )

    def test_publish_notice(self) -> None:
        notice = Notice(
            purpose_id="p1",
            tenant_id="t1",
            translations=(
                NoticeTranslation(
                    locale="en",
                    title="Consent Notice",
                    body_text="We process your data",
                    how_to_withdraw="Withdraw here",
                    how_to_complain_to_dpb="DPB complaints",
                ),
            ),
        )
        published = notice.publish()
        assert published.is_published is True
        assert published.id == notice.id

    def test_new_version_increments_version(self) -> None:
        notice = Notice(
            purpose_id="p1",
            tenant_id="t1",
            translations=(
                NoticeTranslation(
                    locale="en",
                    title="Consent Notice",
                    body_text="We process your data",
                    how_to_withdraw="Withdraw here",
                    how_to_complain_to_dpb="DPB complaints",
                ),
            ),
        )
        new_translations = [
            NoticeTranslation(
                locale="en",
                title="Updated Notice",
                body_text="Updated processing description",
                how_to_withdraw="Click to withdraw",
                how_to_complain_to_dpb="File complaint at dpb.gov.in",
            ),
        ]
        v2 = notice.new_version(new_translations)
        assert v2.version == 2
        assert v2.purpose_id == notice.purpose_id

    def test_get_translation(self) -> None:
        en = NoticeTranslation(
            locale="en",
            title="Notice",
            body_text="Body",
            how_to_withdraw="Withdraw",
            how_to_complain_to_dpb="DPB",
        )
        hi = NoticeTranslation(
            locale="hi",
            title="सूचना",
            body_text="विवरण",
            how_to_withdraw="वापसी",
            how_to_complain_to_dpb="डीपीबी",
        )
        notice = Notice(
            purpose_id="p1",
            tenant_id="t1",
            translations=(en, hi),
        )
        assert notice.get_translation("hi") == hi
        assert notice.get_translation("fr") is None

    def test_indian_languages_defined(self) -> None:
        """Verify all major Indian languages are listed."""
        assert "en" in INDIAN_LANGUAGES
        assert "hi" in INDIAN_LANGUAGES
        assert "ta" in INDIAN_LANGUAGES
        assert "bn" in INDIAN_LANGUAGES
        assert "te" in INDIAN_LANGUAGES
        assert "mr" in INDIAN_LANGUAGES
        assert "gu" in INDIAN_LANGUAGES
        assert "kn" in INDIAN_LANGUAGES
        assert "ml" in INDIAN_LANGUAGES
        assert "pa" in INDIAN_LANGUAGES
