# Backup & Restore Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Automated Online Backup Policy
- SQLite database backups are automatically created daily using `VACUUM INTO` or atomic snapshot copy.
- Backup files are saved to `./backups/temple_backup_YYYYMMDD_HHMMSS.db`.
- Corresponding SHA-256 metadata files are written to `./backups/temple_backup_YYYYMMDD_HHMMSS.json`.

## 2. Integrity Verification
Before restoring any database snapshot, SHA-256 integrity check is performed automatically.
- Programmatic verification: `BackupManager.verify_backup_integrity(backup_filepath)`

## 3. Disaster Recovery Restoration Procedure
1. Stop the application server: `uvicorn app.main:app --stop`
2. Run restore command:
   ```bash
   python -c "import asyncio; from app.core.backup_manager import BackupManager; asyncio.run(BackupManager.restore_database_from_backup('./backups/<BACKUP_FILE>.db'))"
   ```
3. Restart application server: `uvicorn app.main:app --port 8000`
