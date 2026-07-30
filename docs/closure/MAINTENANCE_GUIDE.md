# Maintenance & Operations Guide - Version 2.0.0

## Version Freeze Policy
- **Version 2.0.0**: Current frozen production release.
- **Version 2.1.x**: Reserved exclusively for critical bug fixes and security patches. No structural architectural changes or new feature additions permitted in v2.1.x.
- **Version 3.0**: Reserved for major future feature additions.

## Standard Maintenance Tasks

### 1. Health Monitoring
- Check `/api/v2/health` every 5 minutes.
- Check `/api/v2/health/database` for database connection latency.

### 2. Backup Maintenance & Integrity Audits
- Run `BackupManager.create_database_backup()` daily.
- Run `BackupManager.verify_backup_integrity()` to verify SHA-256 checksum sidecars.

### 3. Log Rotation & Audit Log Monitoring
- Monitor append-only `audit_logs` table.
- Verify `SYNC_START`, `USER_LOGIN`, and `CAMPAIGN_CREATED` events contain valid trace IDs.
