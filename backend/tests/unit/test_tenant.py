"""Tests for the Tenant domain entity."""

import pytest

from src.domain.exceptions import InvalidTenantError
from src.domain.tenant import Tenant


class TestTenant:
    def test_create_valid_tenant(self) -> None:
        tenant = Tenant(
            name="Acme Corp",
            contact_email="dpo@acme.com",
            supported_languages=("en", "hi", "ta"),
        )
        assert tenant.name == "Acme Corp"
        assert tenant.contact_email == "dpo@acme.com"
        assert tenant.supported_languages == ("en", "hi", "ta")
        assert tenant.is_active is True
        assert tenant.id is not None

    def test_create_tenant_empty_name_raises_error(self) -> None:
        with pytest.raises(InvalidTenantError, match="name must not be empty"):
            Tenant(name="", contact_email="dpo@acme.com")

    def test_create_tenant_invalid_email_raises_error(self) -> None:
        with pytest.raises(InvalidTenantError, match="valid contact email"):
            Tenant(name="Acme", contact_email="not-an-email")

    def test_create_tenant_no_languages_raises_error(self) -> None:
        with pytest.raises(InvalidTenantError, match="language"):
            Tenant(name="Acme", contact_email="dpo@acme.com", supported_languages=())

    def test_deactivate_tenant(self) -> None:
        tenant = Tenant(name="Acme", contact_email="dpo@acme.com")
        deactivated = tenant.deactivate()
        assert deactivated.is_active is False
        assert deactivated.id == tenant.id

    def test_update_languages(self) -> None:
        tenant = Tenant(name="Acme", contact_email="dpo@acme.com")
        updated = tenant.update_languages(["en", "bn"])
        assert updated.supported_languages == ("en", "bn")
        assert updated.id == tenant.id

    def test_update_languages_empty_raises_error(self) -> None:
        tenant = Tenant(name="Acme", contact_email="dpo@acme.com")
        with pytest.raises(InvalidTenantError, match="language"):
            tenant.update_languages([])
