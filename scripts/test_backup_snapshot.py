import asyncio
import os
import sys
import json
import sqlite3

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"), override=True)

from app.core.backup_manager import BackupManager


async def main():
    print("Testing BackupManager snapshot creation...")
    meta = await BackupManager.create_database_backup(temple_id="SKSA_MAIN", created_by="ADMIN")
    print("Backup Metadata:")
    print(json.dumps(meta, indent=2))

    filepath = meta["backup_filepath"]
    print(f"\nChecking file existence and size: {filepath}")
    assert os.path.exists(filepath)
    size = os.path.getsize(filepath)
    print(f"File size: {size} bytes ({round(size / (1024 * 1024), 4)} MB)")
    assert size > 0, "Backup file is empty (0 bytes)!"

    print("\nInspecting SQLite tables in backup:")
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print(f"Tables count: {len(tables)}")
    print(f"Tables list: {tables}")

    required_tables = [
        "persons", "visitors", "users", "audit_logs",
        "sync_queue", "broadcast_campaigns", "broadcast_recipients",
        "communication_settings"
    ]
    for t in required_tables:
        assert t in tables, f"Missing table: {t}"
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        cnt = cur.fetchone()[0]
        print(f"  Table '{t}': {cnt} rows")

    conn.close()
    print("\n[SUCCESS] Backup snapshot verified non-empty and containing all required tables & data!")

if __name__ == "__main__":
    asyncio.run(main())
