# Disaster Recovery Guide — Temple Visitor Management System Enterprise Edition v2.0

## 1. Disaster Recovery Objectives
- **Recovery Point Objective (RPO)**: < 24 Hours (daily automated cloud snapshot).
- **Recovery Time Objective (RTO)**: < 15 Minutes (automated dry-run and restore execution).

## 2. Dry-Run Integrity Validation
Before restoring any remote snapshot into production:
1. Download encrypted cloud archive `.db.gz.enc`.
2. Decrypt AES-256 Fernet payload and decompress GZip stream.
3. Validate SHA-256 checksum match against metadata JSON.
4. Execute dry-run validation:
   ```python
   await CloudBackupService.execute_disaster_recovery_restore(backup_id="cloud_backup_latest", dry_run=True)
   ```

## 3. Full Disaster Recovery Restoration
```python
await CloudBackupService.execute_disaster_recovery_restore(backup_id="cloud_backup_latest", dry_run=False)
```
If restoration fails at any point, the engine automatically rolls back to the pre-restore safety copy (`temple.db.pre_restore`).
