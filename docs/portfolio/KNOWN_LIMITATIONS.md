# Known System Limitations (Current v2.0.0 Release)

The following operational characteristics reflect intentional scope boundaries of the current v2.0.0 release:

1. **Third-Party SMS Gateway Dependency**: Broadcast SMS delivery rates depend on third-party SMS aggregator API availability and carrier delivery networks.
2. **Local Backup Snapshot Exporter Output Format**: The `BackupManager` snapshot exporter produces a standalone SQLite `.db` file containing all dumped PostgreSQL tables for zero-dependency offline restoration.
3. **Single Active Sync Server Endpoint**: Mobile client devices sync outbox events against a single primary server base URL (`/api/v2/sync/upload`) per tenant session.
