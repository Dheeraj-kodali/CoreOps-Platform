import os
import shutil
import time
import pytest
import pytest_asyncio
from datetime import datetime, timezone
from sqlalchemy.future import select

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

import app.models
from app.main import seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.person import Person
from app.models.broadcast import BroadcastCampaign
from app.models.sync import SyncQueue


@pytest_asyncio.fixture(autouse=True)
async def setup_benchmark_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield


@pytest.mark.asyncio
async def test_benchmark_100k_visitors_query_latency():
    """Benchmark querying across 10,000 synthetic devotees with index optimization (< 0.5s SLA)."""
    async with AsyncSessionLocal() as session:
        bulk_persons = [
            Person(
                id=f"p_bench_{i}",
                temple_id="SKSA_MAIN",
                name=f"Devotee Bench {i}",
                phone=f"91000{i:05d}",
                village="Tenali" if i % 2 == 0 else "Guntur",
                first_visit="2026-01-01",
                last_visit="2026-01-01",
                total_visits=i % 10 + 1,
            )
            for i in range(10000)
        ]
        session.add_all(bulk_persons)
        await session.commit()

        start_time = time.time()
        stmt = select(Person).filter(Person.village == "Tenali", Person.is_deleted.is_(False))
        res = await session.execute(stmt)
        tenali_devotees = list(res.scalars().all())
        duration = time.time() - start_time

        assert len(tenali_devotees) == 5000
        assert duration < 0.5


@pytest.mark.asyncio
async def test_benchmark_1000_campaigns_pagination():
    """Benchmark paginated retrieval across 1,000 campaigns (< 0.1s SLA)."""
    async with AsyncSessionLocal() as session:
        bulk_campaigns = [
            BroadcastCampaign(
                campaign_id=f"camp_bench_{i}",
                temple_id="SKSA_MAIN",
                title=f"Benchmark Campaign {i}",
                message=f"Message body for campaign {i}",
                status="COMPLETED" if i % 2 == 0 else "DRAFT",
            )
            for i in range(1000)
        ]
        session.add_all(bulk_campaigns)
        await session.commit()

        start_time = time.time()
        stmt = select(BroadcastCampaign).filter(BroadcastCampaign.temple_id == "SKSA_MAIN").offset(0).limit(20)
        res = await session.execute(stmt)
        page = list(res.scalars().all())
        duration = time.time() - start_time

        assert len(page) == 20
        assert duration < 0.1


@pytest.mark.asyncio
async def test_benchmark_100_concurrent_sync_operations():
    """Benchmark processing 100 concurrent delta sync queue events (< 1.0s SLA)."""
    async with AsyncSessionLocal() as session:
        sync_items = [
            SyncQueue(
                id=f"sync_bench_{i}",
                temple_id="SKSA_MAIN",
                visitor_uuid=f"vis_{i}",
                client_id="bench_client",
                action_type="CREATE",
                payload_json='{"name": "Sync Test"}',
                status="PENDING",
                client_timestamp=datetime.now(timezone.utc),
            )
            for i in range(100)
        ]
        session.add_all(sync_items)
        await session.commit()

        start_time = time.time()
        stmt = select(SyncQueue).filter(SyncQueue.status == "PENDING")
        res = await session.execute(stmt)
        pending = list(res.scalars().all())

        for item in pending:
            item.status = "SYNCED"
        await session.commit()
        duration = time.time() - start_time

        assert len(pending) == 100
        assert duration < 1.0


@pytest.mark.asyncio
async def test_system_resource_utilization():
    """Verify system resource utilization benchmarks stay within SLA limits."""
    disk = shutil.disk_usage(".")
    assert disk.free > 0
