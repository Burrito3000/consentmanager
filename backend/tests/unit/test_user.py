"""Tests for the User domain entity with RBAC."""

import pytest

from src.domain.exceptions import InvalidConsentError
from src.domain.user import ROLE_PERMISSIONS, User, UserRole


class TestUser:
    def test_create_owner_user(self) -> None:
        user = User(
            tenant_id="t1",
            email="owner@acme.com",
            password_hash="hashed_pw",
            role=UserRole.OWNER,
        )
        assert user.role == UserRole.OWNER
        assert user.is_active is True
        assert user.has_permission("tenant.manage") is True

    def test_create_user_invalid_email_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="email"):
            User(
                tenant_id="t1",
                email="not-email",
                password_hash="hashed",
            )

    def test_create_user_empty_password_raises_error(self) -> None:
        with pytest.raises(InvalidConsentError, match="Password"):
            User(
                tenant_id="t1",
                email="user@acme.com",
                password_hash="",
            )

    def test_dpo_has_right_permissions(self) -> None:
        user = User(
            tenant_id="t1",
            email="dpo@acme.com",
            password_hash="hashed",
            role=UserRole.DPO,
        )
        assert user.has_permission("purpose.manage") is True
        assert user.has_permission("rights.manage") is True
        assert user.has_permission("audit.view") is True
        assert user.has_permission("tenant.manage") is False

    def test_analyst_read_only(self) -> None:
        user = User(
            tenant_id="t1",
            email="analyst@acme.com",
            password_hash="hashed",
            role=UserRole.ANALYST,
        )
        assert user.has_permission("consent.view") is True
        assert user.has_permission("analytics.view") is True
        assert user.has_permission("purpose.manage") is False
        assert user.has_permission("rights.manage") is False

    def test_auditor_permissions(self) -> None:
        user = User(
            tenant_id="t1",
            email="auditor@acme.com",
            password_hash="hashed",
            role=UserRole.AUDITOR,
        )
        assert user.has_permission("audit.view") is True
        assert user.has_permission("consent.view") is True
        assert user.has_permission("purpose.manage") is False

    def test_change_role(self) -> None:
        user = User(
            tenant_id="t1",
            email="user@acme.com",
            password_hash="hashed",
            role=UserRole.ANALYST,
        )
        dpo = user.change_role(UserRole.DPO)
        assert dpo.role == UserRole.DPO
        assert dpo.id == user.id

    def test_record_login(self) -> None:
        user = User(
            tenant_id="t1",
            email="user@acme.com",
            password_hash="hashed",
            role=UserRole.ANALYST,
        )
        logged_in = user.record_login()
        assert logged_in.last_login_at is not None
        assert logged_in.last_login_at != user.last_login_at

    def test_all_roles_have_expected_permissions(self) -> None:
        """Verify role permission matrix is comprehensive."""
        for role in UserRole:
            perms = ROLE_PERMISSIONS.get(role, set())
            assert len(perms) > 0, f"Role {role} has no permissions"
