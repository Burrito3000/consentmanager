"""Seed script — creates demo tenant with sample purposes, notices, and admin user.

Usage:
    python -m src.infrastructure.seed
"""

from __future__ import annotations

from src.domain.api_key import ApiKey
from src.domain.notice import Notice, NoticeTranslation
from src.domain.principal import DataPrincipal
from src.domain.purpose import LawfulBasis, Purpose
from src.domain.tenant import Tenant
from src.domain.user import User, UserRole
from src.infrastructure.database.uow import SqlUnitOfWork


def seed() -> None:
    """Seed the database with demo data."""
    print("Seeding database...")

    with SqlUnitOfWork() as uow:
        # Check if already seeded
        existing = uow.tenants.list_all()
        if existing:
            print(f"Database already seeded with {len(existing)} tenant(s). Skipping.")
            return

        # 1. Create tenant
        tenant = Tenant(
            name="Acme Corp",
            contact_email="dpo@acme.com",
            supported_languages=("en", "hi", "ta", "bn"),
        )
        uow.tenants.save(tenant)
        uow.flush()
        print(f"  Created tenant: {tenant.name} ({tenant.id})")

        # 2. Create purposes
        purposes_data = [
            {
                "name": "Email Marketing",
                "description": "Send promotional emails about products and offers",
                "data_categories": ("email", "name"),
                "retention_period_days": 365,
                "lawful_basis": LawfulBasis.CONSENT,
            },
            {
                "name": "Order Processing",
                "description": "Process orders, payments, and deliveries",
                "data_categories": ("name", "address", "phone", "payment_info"),
                "retention_period_days": 730,
                "lawful_basis": LawfulBasis.CONTRACT,
            },
            {
                "name": "Analytics & Personalization",
                "description": "Analyze usage patterns to personalize experience",
                "data_categories": ("browsing_history", "device_info", "location"),
                "retention_period_days": 180,
                "lawful_basis": LawfulBasis.CONSENT,
            },
        ]

        purposes = []
        for pd in purposes_data:
            purpose = Purpose(
                tenant_id=tenant.id,
                **pd,
            )
            uow.purposes.save(purpose)
            purposes.append(purpose)
            print(f"  Created purpose: {purpose.name}")

        # 3. Create notices for each purpose (English + Hindi + Tamil)
        for purpose in purposes:
            translations = [
                NoticeTranslation(
                    locale="en",
                    title=f"Consent Notice — {purpose.name}",
                    body_text=(
                        f"We collect and process your personal data for the purpose of {purpose.name.lower()}. "
                        f"This includes the following data categories: {', '.join(purpose.data_categories)}."
                    ),
                    how_to_withdraw=(
                        "You can withdraw your consent at any time by visiting your account settings "
                        "or contacting our Data Protection Officer at dpo@acme.com. "
                        "Withdrawal is as easy as granting consent."
                    ),
                    how_to_complain_to_dpb=(
                        "If you believe your data protection rights have been violated, "
                        "you may file a complaint with the Data Protection Board of India "
                        "at complaints@dpb.gov.in or visit https://dpb.gov.in/complaint."
                    ),
                ),
                NoticeTranslation(
                    locale="hi",
                    title=f"सहमति सूचना — {purpose.name}",
                    body_text=(
                        f"हम {purpose.name.lower()} के उद्देश्य के लिए आपका व्यक्तिगत डेटा एकत्र और संसाधित करते हैं। "
                        f"इसमें डेटा श्रेणियां शामिल हैं: {', '.join(purpose.data_categories)}।"
                    ),
                    how_to_withdraw=(
                        "आप किसी भी समय अपनी खाता सेटिंग में जाकर या हमारे डेटा सुरक्षा अधिकारी "
                        "से dpo@acme.com पर संपर्क करके अपनी सहमति वापस ले सकते हैं। "
                        "सहमति वापस लेना उतना ही आसान है जितना कि सहमति देना।"
                    ),
                    how_to_complain_to_dpb=(
                        "यदि आपको लगता है कि आपके डेटा सुरक्षा अधिकारों का उल्लंघन हुआ है, "
                        "तो आप भारतीय डेटा सुरक्षा बोर्ड में complaints@dpb.gov.in पर "
                        "शिकायत दर्ज कर सकते हैं।"
                    ),
                ),
                NoticeTranslation(
                    locale="ta",
                    title=f"அனுமதி அறிவிப்பு — {purpose.name}",
                    body_text=(
                        f"{purpose.name.lower()} நோக்கத்திற்காக உங்கள் தனிப்பட்ட தரவை நாங்கள் சேகரித்து செயலாக்குகிறோம். "
                        f"இதில் தரவு வகைகள் அடங்கும்: {', '.join(purpose.data_categories)}."
                    ),
                    how_to_withdraw=(
                        "உங்கள் கணக்கு அமைப்புகளுக்குச் சென்று அல்லது dpo@acme.com இல் எங்கள் தரவு பாதுகாப்பு "
                        "அதிகாரியைத் தொடர்புகொள்வதன் மூலம் எந்த நேரத்திலும் உங்கள் ஒப்புதலை திரும்பப் பெறலாம்."
                    ),
                    how_to_complain_to_dpb=(
                        "உங்கள் தரவு பாதுகாப்பு உரிமைகள் மீறப்பட்டதாக நீங்கள் நம்பினால், "
                        "இந்திய தரவு பாதுகாப்பு வாரியத்தில் complaints@dpb.gov.in இல் புகார் செய்யலாம்."
                    ),
                ),
            ]

            notice = Notice(
                purpose_id=purpose.id,
                tenant_id=tenant.id,
                translations=translations,
                is_published=True,
            )
            uow.notices.save(notice)
            print(f"  Created notice for: {purpose.name} ({len(translations)} languages)")

        # 4. Create admin user
        import hashlib

        admin = User(
            tenant_id=tenant.id,
            email="admin@acme.com",
            password_hash=hashlib.sha256(
                b"admin123"
            ).hexdigest(),  # WARNING: Dev-only! Override in production via ADMIN_PASSWORD env var.
            role=UserRole.OWNER,
        )
        uow.users.save(admin)
        print(f"  Created admin user: {admin.email} / admin123")

        # 5. Create DPO user
        dpo = User(
            tenant_id=tenant.id,
            email="dpo@acme.com",
            password_hash=hashlib.sha256(b"dpo123").hexdigest(),  # WARNING: Dev-only!
            role=UserRole.DPO,
        )
        uow.users.save(dpo)
        print(f"  Created DPO user: {dpo.email} / dpo123")

        # 6. Create API key
        api_key = ApiKey(
            tenant_id=tenant.id,
            key_prefix=f"cmp_test_{tenant.id[:8]}",
            key_hash=hashlib.sha256(f"sk_test_{tenant.id}".encode()).hexdigest(),
            label="Demo SDK Key",
            allowed_origins=("http://localhost:3000",),
        )
        uow.api_keys.save(api_key)
        print(f"  Created API key: {api_key.key_prefix}")

        # 7. Create sample data principal
        principal = DataPrincipal(
            tenant_id=tenant.id,
            external_ref="demo-user-001",
            email="user@example.com",
            locale="en",
        )
        uow.principals.save(principal)
        print(f"  Created data principal: {principal.external_ref}")

        uow.commit()

    print("\nSeed complete!")
    print(f"  Tenant ID: {tenant.id}")
    print("  Admin login: admin@acme.com / admin123")
    print("  DPO login: dpo@acme.com / dpo123")
    print(f"  API Key prefix: {api_key.key_prefix}")


if __name__ == "__main__":
    seed()
