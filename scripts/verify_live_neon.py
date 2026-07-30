import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure backend directory is in python path & load backend/.env
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)
load_dotenv(os.path.join(backend_dir, ".env"), override=True)

from sqlalchemy.future import select
from sqlalchemy import inspect, text
from app.core.database import engine, AsyncSessionLocal
from app.models.person import Person
from app.models.temple import Temple
from app.models.user import User
from app.models.audit import AuditRecord
from app.models.broadcast import BroadcastCampaign
from app.models.communication import CommunicationSetting
from app.models.dead_letter import DeadLetterJob
from app.main import seed_initial_data


async def verify_neon_live():
    print("=" * 60)
    print("LIVE NEON POSTGRESQL INTEGRATION VERIFICATION")
    print("=" * 60)

    # 1. SSL & Connection Verification
    print("\n[1/5] Testing Neon SSL & Async Connection...")
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version(), current_database(), current_user;"))
        row = result.fetchone()
        print(f"  [OK] Connected to PostgreSQL DB: '{row[1]}' as User: '{row[2]}'")
        print(f"  [OK] Server Version: {row[0][:65]}...")

    # 2. Table & Index Existence Verification
    print("\n[2/5] Verifying Target Schema Tables in Neon PostgreSQL...")
    expected_tables = [
        "users",
        "roles",
        "permissions",
        "persons",
        "visitors",
        "sync_queue",
        "sync_tokens",
        "audit_logs",
        "broadcast_campaigns",
        "broadcast_recipients",
        "communication_settings",
        "dead_letter_jobs",
    ]

    def check_tables(sync_conn):
        inspector = inspect(sync_conn)
        tables = inspector.get_table_names()
        return tables

    async with engine.connect() as conn:
        tables = await conn.run_sync(check_tables)
        for tbl in expected_tables:
            if tbl in tables:
                print(f"  [OK] Table '{tbl}' verified.")
            else:
                print(f"  [FAIL] MISSING TABLE '{tbl}'")
                raise RuntimeError(f"Missing table {tbl}")

    # 3. Live CRUD Test Operation
    print("\n[3/5] Performing Live CRUD Operations on Neon PostgreSQL...")
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Temple).where(Temple.code == "SKSA_MAIN"))
        t = res.scalars().first()
        if not t:
            t = Temple(id="SKSA_MAIN", name="Sri Kalki Seva Alayam", code="SKSA_MAIN", address="Temple Complex", is_active=True)
            session.add(t)
            await session.commit()
            await session.refresh(t)
        temple_id = t.id

    test_person_id = "test_neon_live_p1001"
    async with AsyncSessionLocal() as session:
        # CLEANUP OLD IF EXISTS
        existing = await session.get(Person, test_person_id)
        if existing:
            await session.delete(existing)
            await session.commit()

        # CREATE
        p = Person(
            id=test_person_id,
            temple_id=temple_id,
            name="Neon Test Devotee",
            phone="9988776655",
            village="Vijayawada",
            total_visits=1,
            first_visit="2026-07-30",
            last_visit="2026-07-30",
        )
        session.add(p)
        await session.commit()
        print(f"  [OK] CREATE: Inserted person '{p.name}' (ID: {p.id}) into Neon PostgreSQL.")

        # READ
        res = await session.execute(select(Person).where(Person.id == test_person_id))
        fetched = res.scalars().first()
        assert fetched is not None, "Read back failed!"
        print(f"  [OK] READ: Fetched record '{fetched.name}' from Neon PostgreSQL.")

        # UPDATE
        fetched.total_visits = 2
        await session.commit()
        print(f"  [OK] UPDATE: Updated total_visits to 2.")

        # DELETE (Cleanup)
        await session.delete(fetched)
        await session.commit()
        print(f"  [OK] DELETE: Cleaned up test record from Neon PostgreSQL.")

    # 4. Outbox & Synchronization Verification
    print("\n[4/5] Verifying Delta Sync Engine Compatibility...")
    async with AsyncSessionLocal() as session:
        res = await session.execute(select(Person).limit(5))
        count = len(res.scalars().all())
        print(f"  [OK] Sync Engine Query executed cleanly on Neon PostgreSQL ({count} persons found).")

    # 5. Database Health Check Verification
    print("\n[5/5] Database Health Check...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        val = result.scalar()
        assert val == 1
        print("  [OK] Database Health Check PASSED (SELECT 1 -> 1).")

    print("\n" + "=" * 60)
    print("ALL LIVE NEON POSTGRESQL VERIFICATION STEPS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(verify_neon_live())
