# Software Requirements Specification (SRS) - v2.0
## Temple Visitor Management System Enterprise Edition

### 1. Introduction
This document defines the formal Software Requirements Specification (SRS) for the **Temple Visitor Management System Enterprise Edition v2.0**.

#### 1.1 Purpose
The system provides offline-first devotee registration, visitor management, broadcast communications, owner analytics, and cloud database synchronization for Sri Kalki Seva Alayam.

#### 1.2 Scope
- **Mobile Edge Application**: Flutter mobile client operating offline on SQLite.
- **Cloud Backend API**: FastAPI asynchronous backend connected to Neon PostgreSQL.
- **Owner Dashboard**: Real-time analytics, visitor trends, sync health, and audit logs.
- **Broadcast System**: Multi-channel (SMS/WhatsApp) targeted broadcast engine.
- **Disaster Recovery**: Automated snapshot backups, SHA-256 integrity verification, and isolated DB restoration.

---

### 2. Original Client Requirements Compliance

| Req ID | Original Client Requirement | Technical Implementation | Compliance |
| :-: | :--- | :--- | :-: |
| **REQ-1** | *"The owner must be able to access every visitor who has ever visited the temple."* | Paginated search & directory API (`GET /api/v1/visitors/`) querying master `persons` and `visitors` records with indexing by name, phone, village, and dates. | **100%** |
| **REQ-2** | *"During important events, the owner must be able to send a custom/default message to all historical visitors or a selected group."* | Audience-filtered broadcast engine (`POST /api/v2/broadcast/campaigns`) supporting `ALL_DEVOTEES`, `VILLAGE_MATCH`, `DATE_RANGE`, `REPEAT_VISITORS` with template library and recipient queuing. | **100%** |
| **REQ-3** | *"The owner must have complete visibility into the entire system at any time."* | Executive Owner Dashboard (`GET /api/v2/dashboard/overview`), real-time visitor analytics, sync metrics, health check endpoints, and 20-field append-only audit trail (`audit_logs`). | **100%** |

---

### 3. Functional Requirements

#### 3.1 Offline Edge Operation
- **FR-1.1**: The mobile app MUST allow volunteer registration of new devotees without network connectivity.
- **FR-1.2**: Every local registration MUST write to local SQLite database and stage an outbox event in local `outbox_events`.
- **FR-1.3**: Outbox event payloads MUST include ISO UTC timestamps, client device IDs, and UUID event keys.

#### 3.2 Delta Synchronization Protocol
- **FR-2.1**: The system MUST process client outbox batches via `POST /api/v2/sync/upload`.
- **FR-2.2**: The backend MUST execute idempotent record upserts into Neon PostgreSQL database.
- **FR-2.3**: Successful synchronization MUST return HTTP 200 with per-event `SYNCED` statuses and issue a new `next_sync_token`.

#### 3.3 Broadcast Messaging System
- **FR-3.1**: The system MUST support audience filtering by village name, visit date range, repeat visit count, or all historical devotees.
- **FR-3.2**: Campaign creation MUST require explicit pre-flight confirmation (`confirmed: True`).
- **FR-3.3**: Recipient dispatch MUST operate asynchronously, updating recipient status in `broadcast_recipients`.

#### 3.4 Owner Visibility & Analytics
- **FR-4.1**: The dashboard MUST calculate real-time totals for live visitors, today's visitors, weekly, monthly, and yearly totals.
- **FR-4.2**: The dashboard MUST break down first-time vs. repeat devotees.
- **FR-4.3**: The system MUST log all administrative actions to an append-only `audit_logs` table with 20 specification fields.

#### 3.5 Backup & Disaster Recovery
- **FR-5.1**: `BackupManager` MUST export all active SQLAlchemy database tables into a standalone SQLite backup `.db` file.
- **FR-5.2**: Snapshot metadata MUST compute and record a SHA-256 checksum sidecar file (`.json`).
- **FR-5.3**: Restoration MUST support verifying database integrity using `PRAGMA integrity_check`.

---

### 4. Non-Functional Requirements

- **NFR-1 (Performance)**: Sync API response latency MUST be under 1,000ms for standard batch sizes.
- **NFR-2 (Security)**: API endpoints MUST enforce JWT authentication (HS256) and tenant isolation headers (`X-Temple-ID`).
- **NFR-3 (Availability)**: Mobile edge client MUST remain 100% operational during cloud server outages.
- **NFR-4 (Data Integrity)**: Audit trail records MUST be immutable (preventing `UPDATE` and `DELETE` queries).
