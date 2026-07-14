# DPDP Consent Management Platform

A production-grade, multi-tenant **Consent Management Platform (CMP)** compliant with India's **Digital Personal Data Protection Act (DPDP) 2023**. Built for Data Fiduciaries to manage consent collection, audit trails, data-principal rights, and grievance redressal.

## Architecture

```
                    ┌─────────────┐
                    │  Next.js 15  │  Frontend (Landing, Dashboard, Admin)
                    │  (App Router)│
                    └──────┬──────┘
                           │ HTTP
              ┌────────────┼────────────┐
              │            │            │
     ┌────────▼───┐ ┌─────▼──────┐ ┌───▼────────┐
     │  FastAPI    │ │  Flask     │ │  JS SDK     │
     │  (Public)   │ │  (Admin)   │ │  (Embed)    │
     └────────┬───┘ └─────┬──────┘ └───┬────────┘
              │            │            │
              └────────────┼────────────┘
                           │
              ┌────────────▼────────────┐
              │    Service Layer         │  Use-cases, orchestration
              │    (Shared Business      │
              │     Logic)               │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │    Domain Layer          │  Pure Python entities & value objects
              │    (Framework-free)      │
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │    Repository Layer      │  ABC interfaces
              └────────────┬────────────┘
                           │
              ┌────────────▼────────────┐
              │    Infrastructure        │  SQLAlchemy, Redis, Celery, Crypto
              │    (Implementations)     │
              └─────────────────────────┘
```

**Key Decision:** Admin portal is served via **Flask (Jinja templates)** instead of Next.js for the admin/compliance portal. Rationale: DPO/auditor consoles are internal tools with simpler UI needs; Flask keeps the backend monolith cohesive (same process, shared service instances), avoids duplicating API client logic in Next.js for every admin action, and provides faster iteration for data-grid-heavy pages. If the team grows, a separate admin SPA can be added later — the service layer remains identical.

## DPDP Compliance Features

- ✅ **Free, specific, informed, unconditional, unambiguous** consent per-purpose (no bundled consent)
- ✅ **Explicit affirmative action** — no pre-ticked boxes
- ✅ **Withdrawal as easy as grant** — one-click withdrawal that fires webhooks
- ✅ **Multilingual notices** — English + selectable Indian languages
- ✅ **Append-only event log** — tamper-evident hash chain (SHA-256)
- ✅ **7-year retention** for consent records + audit logs
- ✅ **Data-principal rights endpoints** — access, correction, erasure, grievance, nominee, withdraw
- ✅ **SLA timers** — 90 days (rights), configurable (grievance)
- ✅ **Data minimization** — store consent metadata, not raw personal data
- ✅ **Audit-ready** — full request/response logging, hash-chain verification

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Public API** | FastAPI (async, Pydantic v2, auto OpenAPI) |
| **Admin Portal** | Flask + Jinja + Gunicorn |
| **Domain/Service** | Pure Python 3.12+, Dependency Injection |
| **Database** | PostgreSQL 16 (Alembic migrations) |
| **Cache/Queue** | Redis 7 |
| **Task Worker** | Celery (webhooks, emails, retention jobs) |
| **Encryption** | AES-256-GCM at rest, JWT for tokens, HMAC for artifacts |
| **Frontend** | Next.js 15 App Router + TypeScript + Tailwind + shadcn/ui |
| **SDK** | Vanilla TypeScript → IIFE embed, React wrapper |
| **Monitoring** | structlog, health endpoints |
| **Infra** | Docker Compose (local), AWS ECS/RDS/ElastiCache (prod) |

## Project Structure

```
├── backend/
│   ├── src/
│   │   ├── domain/           # Pure entities & value objects
│   │   ├── repositories/     # ABC interfaces
│   │   ├── services/         # Use-case orchestration
│   │   ├── infrastructure/   # SQLAlchemy, Redis, Celery, crypto
│   │   ├── api/              # FastAPI routes (thin controllers)
│   │   ├── admin/            # Flask admin portal
│   │   └── config/           # Pydantic Settings
│   ├── tests/
│   ├── alembic/
│   ├── requirements/
│   └── Dockerfile
├── frontend/
│   ├── app/                  # Next.js 15 App Router pages
│   ├── components/           # Shared components (shadcn/ui)
│   ├── lib/                  # Utilities, API client
│   ├── public/
│   └── Dockerfile
├── sdk/
│   ├── src/                  # Vanilla TS consent SDK
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start (Local Dev)

### Prerequisites

- Docker & Docker Compose v2
- Python 3.12+ (for IDE support)
- Node.js 22+ (for frontend)
- Just `make` (optional)

### 1. Clone and environment

```bash
cp .env.example .env
# Edit .env with your secrets (see Security section)
```

### 2. Start all services

```bash
docker compose up -d
```

This starts: postgres, redis, api (FastAPI :8000), admin (Flask :8001), worker (Celery), beat (Celery scheduler), web (Next.js :3000).

### 3. Run migrations

```bash
docker compose exec api alembic upgrade head
```

### 4. Seed demo data

```bash
docker compose exec api python -m src.infrastructure.seed
```

### 5. Access

| Service | URL |
|---------|-----|
| Public API | http://localhost:8000/docs (Swagger) |
| Admin Portal | http://localhost:8001/admin/ |
| Frontend | http://localhost:3000 |

### 6. Run tests

```bash
# Backend
docker compose exec api pytest --cov=src

# Frontend
cd frontend && npm test

# SDK
cd sdk && npm test
```

## Security

- ✅ **TLS everywhere** — terminated at ALB/CloudFront in prod
- ✅ **AES-256-GCM** at rest for sensitive DB columns
- ✅ **Per-tenant API keys** + scoped JWT SDK tokens (15-min TTL)
- ✅ **RBAC** — Owner, DPO, Analyst, Auditor roles
- ✅ **Rate limiting** — 60 req/min per tenant
- ✅ **Input validation** — Pydantic v2 schemas
- ✅ **CORS** — locked to tenant-registered origins
- ✅ **OWASP ASVS baseline** — security headers, CSP, no secrets in logs

### Environment Secrets

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | 64-char random string for Flask/FastAPI |
| `ENCRYPTION_KEY` | 32-byte base64-encoded AES key |
| `JWT_SECRET` | 64-char random string for token signing |
| `DATABASE_URL` | Postgres DSN |
| `REDIS_URL` | Redis DSN |

Generate keys:
```bash
python -c "import secrets, base64; print(base64.b64encode(secrets.token_bytes(32)).decode())"
```

## Deployment: AWS ap-south-1 (Mumbai)

See [deploy/aws.md](docs/deploy/aws.md) for full guide.

High-level:
1. **RDS PostgreSQL** — multi-AZ, encrypted, automated backups
2. **ElastiCache Redis** — for Celery + caching
3. **ECS Fargate** — api, admin, worker services
4. **CloudFront + S3** — Next.js static assets
5. **ALB** — TLS termination (ACM certs)
6. **Secrets Manager** — all secrets
7. **WAF** — rate limiting, IP allowlisting

## License

Proprietary. All rights reserved.

---
**⚠️ Legal Notice:** This platform implements DPDP Act 2023 requirements to the best of engineering ability. However, the final compliance determination must be made by qualified legal counsel. Sections flagged with `# DPDP_LEGAL_REVIEW` in source code indicate areas where the specific wording from DPDP Rules / Schedule I should be verified against the latest gazette notification.
****
