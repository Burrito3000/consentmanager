"""Tests for the ApiKey domain entity."""

from datetime import UTC, datetime, timedelta

import pytest

from src.domain.api_key import ApiKey
from src.domain.exceptions import InvalidConsentError


class TestApiKey:
    def test_create_valid_api_key(self) -> None:
        key = ApiKey(
            tenant_id="t1",
            key_prefix="cmp_live_abc",
            key_hash="$2b$12$hashed_value",
            label="Production SDK Key",
        )
        assert key.tenant_id == "t1"
        assert key.is_active is True
        assert key.is_expired() is False

    def test_api_key_without_tenant_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="Tenant"):
            ApiKey(
                tenant_id="",
                key_prefix="pre",
                key_hash="hash",
                label="Test",
            )

    def test_api_key_without_hash_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="hash"):
            ApiKey(
                tenant_id="t1",
                key_prefix="pre",
                key_hash="",
                label="Test",
            )

    def test_expired_api_key(self) -> None:
        past = datetime.now(UTC) - timedelta(days=1)
        key = ApiKey(
            tenant_id="t1",
            key_prefix="pre",
            key_hash="hash",
            label="Expired Key",
            expires_at=past,
        )
        assert key.is_expired() is True

    def test_origin_allowlist_no_restrictions(self) -> None:
        key = ApiKey(
            tenant_id="t1",
            key_prefix="pre",
            key_hash="hash",
            label="Open Key",
            allowed_origins=(),
        )
        assert key.is_origin_allowed("https://evil.com") is True

    def test_origin_allowlist_with_restrictions(self) -> None:
        key = ApiKey(
            tenant_id="t1",
            key_prefix="pre",
            key_hash="hash",
            label="Restricted Key",
            allowed_origins=("https://app.acme.com", "https://admin.acme.com"),
        )
        assert key.is_origin_allowed("https://app.acme.com") is True
        assert key.is_origin_allowed("https://evil.com") is False

    def test_deactivate_api_key(self) -> None:
        key = ApiKey(
            tenant_id="t1",
            key_prefix="pre",
            key_hash="hash",
            label="Test Key",
        )
        deactivated = key.deactivate()
        assert deactivated.is_active is False
        assert deactivated.id == key.id
