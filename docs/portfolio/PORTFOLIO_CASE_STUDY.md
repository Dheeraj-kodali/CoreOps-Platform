# Portfolio Case Study: Temple Visitor Management System Enterprise Edition

## 1. Problem Statement
Sri Kalki Seva Alayam experienced high-volume devotee traffic during festivals and peak days. Edge registration terminals frequently suffered from unreliable internet access, leading to data loss, long queues, and fragmented records. Temple administrators lacked real-time visibility into attendance trends, sync queue health, and broadcast notification capabilities.

## 2. Technical Solution
We engineered a dual-layer offline-first architecture:
- **Mobile Edge Application**: Built with Flutter (Dart) and SQLite edge storage. Client terminals write devotee mutations locally using a Transactional Outbox pattern, enabling 100% offline uptime.
- **Delta Synchronization Gateway**: Designed a FastAPI server gateway (`POST /api/v2/sync/upload`) that ingests client event batches, executes idempotent upserts against a serverless **Neon PostgreSQL 18** cloud database, and issues unique `next_sync_token` tracking headers.
- **Targeted Broadcast Messaging Engine**: Built an audience-filtering engine supporting `ALL_DEVOTEES`, `VILLAGE_MATCH`, `DATE_RANGE`, and `REPEAT_VISITORS` with template management and delivery status tracking.
- **Executive Visibility & Auditability**: Delivered an Owner Dashboard API (`/overview`, `/visitor-analytics`, `/sync-metrics`) and a 20-field append-only audit trail (`audit_logs`) protected by SQLAlchemy ORM event hooks.
- **Backup & Disaster Recovery**: Built `BackupManager` snapshot exporter producing standalone SQLite `.db` backups with SHA-256 integrity sidecars, AES-256 Fernet encryption, and DR restore verification.

## 3. Quantifiable Results & Impact
- **0% Edge Downtime**: 100% registration availability during network blackouts.
- **100% Sync Accuracy**: Zero duplicate records during duplicate event retry tests.
- **100% Test Pass Rate**: Verified across 104 total automated unit, integration, acceptance, and disaster recovery tests.
