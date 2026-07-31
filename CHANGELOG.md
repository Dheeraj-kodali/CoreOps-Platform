# Changelog

All notable changes to the **Temple Management Platform** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [v1.0.0] - 2026-07-31

### Added
- **Flutter Offline Mobile App (`mobile/`)**: Offline-first visitor registration client operating on SQLite with Transactional Outbox synchronization pattern.
- **FastAPI Production Backend (`backend/`)**: High-performance asynchronous REST API supporting multi-tenant isolation, PBKDF2-SHA256 password hashing, JWT authentication, and append-only audit trail logging (`AuditRecord`).
- **Next.js 15 Admin Web Portal (`admin-web/`)**: Browser-based owner dashboard built with Next.js 15, TypeScript, Tailwind CSS, TanStack Query, featuring 6 core sections:
  - **Live Executive Dashboard**: KPI cards, recent check-ins, visitor velocity charts, purpose analytics.
  - **Enterprise Visitor Management**: Live visitor table, multi-select batch operations, full profile side drawer, CSV export, print badges.
  - **Analytics Reports & Audit Center**: Custom date selectors, PDF/Excel/CSV exports, immutable audit trail filters.
  - **Enterprise User & Role Management**: Staff table, Create User, Activate/Deactivate toggles, Reset Password, Reset PIN, Role Permission Matrix.
  - **Temple Settings & Branding**: Organization profile, primary/secondary color pickers, operating hours, custom report receipt branding.
  - **Communication & Broadcast Center**: WhatsApp campaign composer, audience filters, message previewer, scheduled broadcasts, retry failed dispatches.
  - **Security Center**: Security score health (96%), active session revocation ("Logout From All Devices"), login attempt log, TOTP MFA readiness.
  - **Operations Center**: System health ping, DB connection pool status, live memory/CPU/disk monitors, 24-hour background scheduler, physical SQL backup generator, 30-day retention policy, and backup snapshot downloader.

### Security
- Implemented PBKDF2-SHA256 password hashing and strict password complexity rules.
- Enforced JWT token expiration and JTI revocation check.
- Added tenant isolation middleware (`X-Temple-ID`) and security HTTP headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`).
- Protected audit logs with SQLAlchemy event listeners preventing modification or deletion of historical records.

---

## [v0.9.0] - 2026-07-28
- Pre-release build of mobile outbox sync protocol and Neon PostgreSQL cloud database integration.
