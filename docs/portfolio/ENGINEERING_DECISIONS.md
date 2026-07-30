# Engineering Trade-Offs & Architecture Decisions

### Decision 1: SQLite Edge + Neon PostgreSQL Hybrid vs. Pure Cloud DB
- **Choice**: SQLite offline storage at client edge + Neon PostgreSQL serverless cloud DB.
- **Trade-off**: Requires maintaining a synchronization engine (`POST /api/v2/sync/upload`) and conflict resolution logic.
- **Rationale**: Temple terminals operate in low-connectivity areas where internet blackouts are common. 100% offline edge uptime was a non-negotiable operational requirement.

### Decision 2: Transactional Outbox Pattern vs. Live REST Direct Writes
- **Choice**: Stage all edge mutations in local `outbox_events` SQLite table first.
- **Trade-off**: Requires background sync workers and client token tracking.
- **Rationale**: Guarantees zero data loss on mobile devices even if the device crashes or powers down before network transmission.

### Decision 3: Append-Only Immutable Audit Trail via SQLAlchemy Hooks
- **Choice**: Hook into SQLAlchemy ORM `before_compile` to block `UPDATE` and `DELETE` queries on `audit_logs`.
- **Trade-off**: Audit logs grow monotonically over time.
- **Rationale**: Ensures complete regulatory compliance and non-repudiation for administrative actions.
