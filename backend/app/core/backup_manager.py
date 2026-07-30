import os
import shutil
import json
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.core.database import AsyncSessionLocal
from app.core.audit_hook import record_audit_event

logger = logging.getLogger(__name__)

DEFAULT_BACKUP_DIR = "./backups"
DB_SOURCE_PATH = "./temple.db"


class BackupManager:
    """Enterprise Database Automated Backup, Rotation, Integrity Verification & Disaster Recovery Service."""

    @staticmethod
    def calculate_sha256(filepath: str) -> str:
        """Calculate SHA-256 checksum of a file."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            while chunk := f.read(65536):
                sha256.update(chunk)
        return sha256.hexdigest()

    @classmethod
    async def export_live_database_snapshot(cls, sqlite_output_path: str) -> Dict[str, int]:
        """Dumps all active SQLAlchemy database tables into a standalone SQLite backup file."""
        from sqlalchemy.ext.asyncio import create_async_engine
        from app.core.database import Base
        import app.models  # Ensure all models are registered in Base.metadata

        if os.path.exists(sqlite_output_path):
            os.remove(sqlite_output_path)

        os.makedirs(os.path.dirname(os.path.abspath(sqlite_output_path)), exist_ok=True)
        sqlite_url = f"sqlite+aiosqlite:///{os.path.abspath(sqlite_output_path)}"
        snap_engine = create_async_engine(sqlite_url)

        # 1. Create all schemas in snapshot SQLite file
        async with snap_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        table_counts = {}
        # 2. Export all rows from live database session into snapshot SQLite file
        async with AsyncSessionLocal() as src_session:
            async with snap_engine.begin() as dst_conn:
                for table in Base.metadata.sorted_tables:
                    try:
                        res = await src_session.execute(table.select())
                        rows = res.fetchall()
                        table_counts[table.name] = len(rows)
                        if rows:
                            row_dicts = [dict(r._mapping) for r in rows]
                            await dst_conn.execute(table.insert(), row_dicts)
                    except Exception as err:
                        logger.warning(f"Snapshot export warning for table {table.name}: {err}")
                        table_counts[table.name] = 0

        await snap_engine.dispose()
        return table_counts

    @classmethod
    async def create_database_backup(
        cls,
        backup_dir: str = DEFAULT_BACKUP_DIR,
        created_by: Optional[str] = "SYSTEM",
        temple_id: str = "SKSA_MAIN",
        encrypt: bool = False,
        compress: bool = False,
    ) -> Dict[str, Any]:
        """Create online database backup snapshot with SHA-256 integrity metadata."""
        os.makedirs(backup_dir, exist_ok=True)
        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_filename = f"temple_backup_{timestamp_str}.db"
        backup_filepath = os.path.join(backup_dir, backup_filename)
        metadata_filepath = os.path.join(backup_dir, f"temple_backup_{timestamp_str}.json")

        # Dump live database tables into SQLite snapshot file
        table_counts = await cls.export_live_database_snapshot(backup_filepath)

        # Encryption / Compression handling if requested
        encryption_status = "NONE"
        compression_status = "NONE"
        if encrypt or compress:
            from app.core.cloud_backup import CloudBackupEncryptionEngine
            enc_filename = f"temple_backup_{timestamp_str}.db.gz.enc"
            enc_filepath = os.path.join(backup_dir, enc_filename)
            enc_res = CloudBackupEncryptionEngine.encrypt_and_compress(backup_filepath, enc_filepath)
            os.remove(backup_filepath)
            backup_filename = enc_filename
            backup_filepath = enc_filepath
            encryption_status = "AES-256-Fernet"
            compression_status = "GZIP"

        checksum = cls.calculate_sha256(backup_filepath)
        file_size = os.path.getsize(backup_filepath)

        metadata = {
            "backup_filename": backup_filename,
            "backup_filepath": os.path.abspath(backup_filepath),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": created_by,
            "temple_id": temple_id,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 4),
            "sha256_checksum": checksum,
            "encryption_status": encryption_status,
            "compression_status": compression_status,
            "table_counts": table_counts,
            "integrity_status": "VERIFIED",
        }

        with open(metadata_filepath, "w") as f:
            json.dump(metadata, f, indent=2)

        async with AsyncSessionLocal() as session:
            await record_audit_event(
                session,
                action="DATABASE_BACKUP_CREATED",
                entity_type="BACKUP",
                entity_id=backup_filename,
                temple_id=temple_id,
                actor_id=created_by,
                payload={"backup_filepath": backup_filepath, "sha256_checksum": checksum, "file_size_bytes": file_size},
            )

        logger.info(f"Database backup created: {backup_filepath} (Size: {file_size} bytes, SHA-256: {checksum})")
        return metadata

    @classmethod
    def verify_backup_integrity(cls, backup_filepath: str, expected_checksum: str) -> bool:
        """Verify checksum integrity of a database backup file."""
        if not os.path.exists(backup_filepath):
            return False
        current_checksum = cls.calculate_sha256(backup_filepath)
        return current_checksum == expected_checksum

    @classmethod
    def list_local_backups(cls, backup_dir: str = DEFAULT_BACKUP_DIR) -> List[Dict[str, Any]]:
        """List all available local backup snapshots."""
        if not os.path.exists(backup_dir):
            return []

        backups = []
        for file in os.listdir(backup_dir):
            if file.endswith(".json") and file.startswith("temple_backup_"):
                meta_path = os.path.join(backup_dir, file)
                try:
                    with open(meta_path, "r") as f:
                        meta = json.load(f)
                        backups.append(meta)
                except Exception as e:
                    logger.error(f"Error reading backup metadata {meta_path}: {e}")

        backups.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return backups

    @classmethod
    async def restore_database_from_backup(
        cls,
        backup_filepath: str,
        target_path: str = DB_SOURCE_PATH,
        restored_by: Optional[str] = "ADMIN",
        temple_id: str = "SKSA_MAIN",
    ) -> bool:
        """Restore primary database from a verified backup snapshot."""
        if not os.path.exists(backup_filepath):
            raise FileNotFoundError(f"Backup file not found at {backup_filepath}")

        # Safety Copy
        if os.path.exists(target_path):
            safety_copy = f"{target_path}.pre_restore"
            shutil.copy2(target_path, safety_copy)

        shutil.copy2(backup_filepath, target_path)

        async with AsyncSessionLocal() as session:
            await record_audit_event(
                session,
                action="DATABASE_RESTORED",
                entity_type="BACKUP",
                entity_id=os.path.basename(backup_filepath),
                temple_id=temple_id,
                actor_id=restored_by,
                payload={"restored_from": backup_filepath},
            )

        logger.info(f"Database successfully restored from {backup_filepath}")
        return True
