# Enterprise System Architecture — Temple Visitor Management System v2.0

```
+-------------------------------------------------------------+
|                  Flutter Mobile Client                      |
|           (SQLite Primary Offline Local Database)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     Transactional Outbox                    |
|             (Atomic Local Event Registration)               |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Delta Synchronization                     |
|           (HTTP/2 Batch Sync & Conflict Engine)            |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                     FastAPI Backend v2                      |
|          (RBAC, JWT, Audit Hook & Broadcast Engine)         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Neon PostgreSQL Database                  |
|          (Serverless Pooled Multi-Tenant Database)          |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                   Encrypted Cloud Backup                    |
|        (GZip + AES-256 Fernet Multi-Cloud Snapshots)        |
+-------------------------------------------------------------+
```

## Key Architectural Principles
1. **Offline-First Resilience**: Mobile clients read and write locally to SQLite. Network dropouts do not interrupt visitor check-in or checkout.
2. **Transactional Outbox Guarantee**: Registration and sync queue entries are written atomically within a single SQLite transaction.
3. **Delta Sync Protocol**: Transfers only incremental changes (delta timestamps) between SQLite and Neon PostgreSQL.
4. **Neon PostgreSQL Cloud Backend**: Serverless PostgreSQL database powering backend API queries, analytics, and Owner Dashboard features.
5. **Encrypted Snapshot Backups**: Periodic whole-database snapshot backups compressed via GZip and encrypted via Fernet AES-256 uploaded to pluggable cloud storage targets.
