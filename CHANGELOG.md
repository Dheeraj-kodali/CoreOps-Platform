# Changelog

All notable changes to the Temple Visitor Management System Enterprise Edition will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-07-30

### Added
- Integrated live serverless Neon PostgreSQL 18 database with async connection pooling.
- Developed Delta Synchronization Engine (`POST /api/v2/sync/upload`) with sync tokens.
- Implemented Transactional Outbox pattern on mobile edge SQLite database.
- Created Enterprise Broadcast Messaging Engine with audience filters (`ALL_DEVOTEES`, `VILLAGE_MATCH`, `DATE_RANGE`, `REPEAT_VISITORS`).
- Implemented 20-field append-only Immutable Audit trail (`audit_logs`) with UUID trace IDs.
- Built Executive Owner Dashboard API (`/overview`, `/visitor-analytics`, `/sync-metrics`, `/communication-metrics`).
- Developed `BackupManager` snapshot exporter with SHA-256 integrity metadata, Fernet AES-256 encryption, GZIP compression, and isolated DB restore test framework.
- Added JWT JTI token revocation blacklist and security headers (`X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`).

### Changed
- Standardized multi-tenant context enforcement via mandatory `X-Temple-ID` header.
- Updated `AnalyticsService` to use safe property getters for visitor and person records.

### Fixed
- Fixed Alembic migration column size for PostgreSQL version tracking.
- Resolved AsyncPG SSL connection URL parameter formatting (`sslmode=require` -> `ssl=require`).
- Fixed SQLite database table lock during pytest suite teardown.
