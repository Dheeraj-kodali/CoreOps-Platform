# Release Notes - v2.0.0
## Temple Visitor Management System Enterprise Edition

**Release Date**: July 30, 2026  
**Version**: `v2.0.0`

---

### Highlights & Major Capabilities

- **Offline-First SQLite Edge Engine**: Full offline registration and outbox event staging on client terminals.
- **Serverless Neon PostgreSQL 18 Integration**: Live cloud backend database with SSL encryption (`sslmode=require`) and multi-tenant scoping (`X-Temple-ID`).
- **Transactional Outbox & Delta Sync**: Idempotent batch event sync protocol via `POST /api/v2/sync/upload`.
- **Targeted Broadcast Engine**: Audience filtering (`ALL_DEVOTEES`, `VILLAGE_MATCH`, `DATE_RANGE`, `REPEAT_VISITORS`), festival message template library, and recipient status tracking.
- **Owner Dashboard & Immutable Audit**: Real-time visitor counts, sync metrics, communication analytics, health endpoints, and 20-field append-only audit trail.
- **Cloud Backup & Disaster Recovery**: Live database snapshot exporter (`.db`), Fernet AES-256 encryption, GZIP compression, SHA-256 integrity verification, and isolated DB restore test suite.

---

### Quality & Test Verification

- **Backend Pytest Suite**: 57 / 57 PASSED (100%)
- **Flutter Test Suite**: 12 / 12 PASSED (100%)
- **Production Acceptance Suite**: 15 / 15 PASSED (100%)
- **Independent Validation Suite**: 13 / 13 PASSED (100%)
- **Backup & Disaster Recovery Suite**: 7 / 7 PASSED (100%)
- **Client Requirement Compliance**: 100% Full Compliance
