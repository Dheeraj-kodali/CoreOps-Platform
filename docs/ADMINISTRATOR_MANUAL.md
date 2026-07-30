# Administrator Manual - v2.0
## Temple Visitor Management System Enterprise Edition

### 1. Introduction & Administrative Responsibilities
This manual provides system administrators and temple managers with operational instructions for configuring, managing, monitoring, backing up, and maintaining the Temple Visitor Management System.

---

### 2. Environment Configuration & Database Connections
The backend requires environment variables configured in `backend/.env`.

#### Key Configuration Keys
- `DATABASE_URL`: Asynchronous connection string for Neon PostgreSQL (e.g. `postgresql+asyncpg://user:pass@ep-hostname.aws.neon.tech/neondb?sslmode=require`).
- `SYNC_DATABASE_URL`: Synchronous connection string used by Alembic migrations (e.g. `postgresql://user:pass@ep-hostname.aws.neon.tech/neondb?sslmode=require`).
- `SECRET_KEY`: Cryptographic signing key for JWT tokens.
- `BACKUP_ENCRYPTION_KEY`: 32-byte secret key for AES-256 backup encryption.

---

### 3. Database Migration Procedures
To apply Alembic migrations against the live database:
```bash
cd backend
alembic upgrade head
```

To verify Alembic version state:
```bash
alembic current
```

---

### 4. Backup & Disaster Recovery Operations

#### 4.1 Creating Automated Snapshot Backups
Administrators can initiate snapshot creation programmatically or via CLI runner:
```python
from app.core.backup_manager import BackupManager

# Generates standalone SQLite .db snapshot containing all tables and metadata
metadata = await BackupManager.create_database_backup(temple_id="SKSA_MAIN", created_by="ADMIN")
```
Snapshot files are written to `./backups/temple_backup_YYYYMMDD_HHMMSS.db` alongside JSON sidecar metadata containing SHA-256 checksums.

#### 4.2 Verifying Checksum Integrity
```python
is_valid = BackupManager.verify_backup_integrity(backup_filepath, expected_checksum)
```

#### 4.3 Disaster Recovery Restore Procedure
1. Execute restore in an isolated staging DB first:
   ```python
   await BackupManager.restore_database_from_backup(backup_filepath, target_path="./temp_restored.db")
   ```
2. Verify SQLite integrity:
   ```sqlite
   PRAGMA integrity_check;
   PRAGMA foreign_key_check;
   ```

---

### 5. Monitoring & Operational Health Check
- Health Endpoint: `GET /api/v2/health`
- Database Latency Endpoint: `GET /api/v2/health/database`
- Owner Overview Endpoint: `GET /api/v2/dashboard/overview`
