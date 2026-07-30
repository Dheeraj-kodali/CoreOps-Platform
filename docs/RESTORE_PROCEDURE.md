# Restore Procedure — Temple Visitor Management System Enterprise Edition v2.0

## 1. Step-by-Step Restoration Protocol

### Step 1: Select Restore Target
Identify the `backup_id` from the Admin Operations Dashboard or `/health/cloud-backup` health endpoint.

### Step 2: Run Dry-Run Validation Command
```bash
python -c "import asyncio; from app.core.cloud_backup import CloudBackupService; print(asyncio.run(CloudBackupService.execute_disaster_recovery_restore('cloud_backup_latest', dry_run=True)))"
```

### Step 3: Execute Production Restore
```bash
python -c "import asyncio; from app.core.cloud_backup import CloudBackupService; print(asyncio.run(CloudBackupService.execute_disaster_recovery_restore('cloud_backup_latest', dry_run=False)))"
```

### Step 4: Validate Database & Restart Server
Run `pytest tests/test_api.py` and restart the application service: `uvicorn app.main:app --port 8000`.
