"""Tests for the Purpose domain entity."""

import pytest

from src.domain.exceptions import InvalidPurposeError
from src.domain.purpose import LawfulBasis, Purpose


class TestPurpose:
    def test_create_valid_purpose(self) -> None:
        purpose = Purpose(
            tenant_id="tenant-1",
            name="Email Marketing",
            description="Send promotional emails",
            data_categories=("email", "name"),
            retention_period_days=365,
            lawful_basis=LawfulBasis.CONSENT,
        )
        assert purpose.name == "Email Marketing"
        assert purpose.retention_period_days == 365
        assert purpose.is_active is True
        assert purpose.version == 1

    def test_create_purpose_empty_name_raises_error(self) -> None:
        with pytest.raises(InvalidPurposeError, match="name must not be empty"):
            Purpose(
                tenant_id="tenant-1",
                name="",
                description="Test",
                data_categories=("email",),
                retention_period_days=30,
            )

    def test_create_purpose_no_data_categories_raises_error(self) -> None:
        with pytest.raises(InvalidPurposeError, match="data category"):
            Purpose(
                tenant_id="tenant-1",
                name="Test",
                description="Test",
                data_categories=(),
                retention_period_days=30,
            )

    def test_create_purpose_zero_retention_raises_error(self) -> None:
        with pytest.raises(InvalidPurposeError, match="Retention"):
            Purpose(
                tenant_id="tenant-1",
                name="Test",
                description="Test",
                data_categories=("email",),
                retention_period_days=0,
            )

    def test_create_purpose_no_tenant_id_raises_error(self) -> None:
        with pytest.raises(InvalidPurposeError, match="Tenant"):
            Purpose(
                tenant_id="",
                name="Test",
                description="Test",
                data_categories=("email",),
                retention_period_days=30,
            )

    def test_deactivate_purpose(self) -> None:
        purpose = Purpose(
            tenant_id="tenant-1",
            name="Marketing",
            description="Email marketing",
            data_categories=("email",),
            retention_period_days=90,
        )
        deactivated = purpose.deactivate()
        assert deactivated.is_active is False
        assert deactivated.id == purpose.id

    def test_purpose_version_bump(self) -> None:
        purpose = Purpose(
            tenant_id="tenant-1",
            name="Marketing",
            description="Email marketing",
            data_categories=("email",),
            retention_period_days=90,
        )
        v2 = purpose.with_version(2)
        assert v2.version == 2
        assert v2.id == purpose.id

    def test_mandatory_purpose_still_requires_individual_toggle(self) -> None:
        """DPDP: mandatory purposes still require individual notice/toggle.
        This is enforced at consent-grant time, not at purpose creation."""
        purpose = Purpose(
            tenant_id="tenant-1",
            name="Required Analytics",
            description="Essential analytics",
            data_categories=("usage_data",),
            retention_period_days=30,
            is_mandatory=True,
        )
        assert purpose.is_mandatory is True
