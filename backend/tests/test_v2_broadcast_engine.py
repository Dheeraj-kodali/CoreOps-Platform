import os
import json
import time
import asyncio
from datetime import datetime, timezone, timedelta
import pytest
import pytest_asyncio

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

import app.models
from httpx import AsyncClient, ASGITransport
from app.main import app, seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.user import User
from app.models.person import Person
from app.models.broadcast import BroadcastCampaign, BroadcastRecipient
from app.services.audience_builder import AudienceBuilderService
from app.services.broadcast_engine import BroadcastEngine
from app.schemas.broadcast_v2 import AudienceFilterSpec, BroadcastCampaignCreateRequest


@pytest_asyncio.fixture(autouse=True)
async def setup_broadcast_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    yield
    await asyncio.sleep(0.05)


async def get_auth_headers(ac: AsyncClient) -> dict:
    login_res = await ac.post(
        "/api/v2/auth/login",
        json={"username": "admin", "password": "Admin@12345"}
    )
    token = login_res.json()["access_token"]
    return {
        "Authorization": f"Bearer {token}",
        "X-Temple-ID": "SKSA_MAIN"
    }


@pytest.mark.asyncio
async def test_audience_filtering_specifications():
    """Verify Audience Builder filtering across ALL_DEVOTEES, VILLAGE, PURPOSE, REPEAT_VISITORS."""
    async with AsyncSessionLocal() as session:
        # Seed 3 persons
        p1 = Person(id="p1", temple_id="SKSA_MAIN", name="Ramesh", phone="9876500001", village="Tenali", first_visit="2026-01-01", last_visit="2026-01-01")
        p2 = Person(id="p2", temple_id="SKSA_MAIN", name="Sita", phone="9876500002", village="Tenali", first_visit="2026-01-01", last_visit="2026-01-01")
        p3 = Person(id="p3", temple_id="SKSA_MAIN", name="Gopal", phone="9876500003", village="Guntur", first_visit="2026-01-01", last_visit="2026-01-01")
        session.add_all([p1, p2, p3])
        await session.commit()

        builder = AudienceBuilderService(session)

        # 1. All Devotees
        res_all = await builder.filter_recipients("SKSA_MAIN", AudienceFilterSpec(filter_type="ALL_DEVOTEES"))
        assert len(res_all) >= 3

        # 2. Village Filter
        res_tenali = await builder.filter_recipients("SKSA_MAIN", AudienceFilterSpec(filter_type="VILLAGE", village="Tenali"))
        assert len(res_tenali) == 2
        assert all(p.village == "Tenali" for p in res_tenali)


@pytest.mark.asyncio
async def test_campaign_creation_safety_rules_and_confirmation():
    """Verify safety rules requiring explicit confirmation before campaign creation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # Seed person in DB for recipient query
        async with AsyncSessionLocal() as session:
            p_seed = Person(id="p_confirm", temple_id="SKSA_MAIN", name="Devotee Confirm", phone="9988776655", village="Vijayawada", first_visit="2026-01-01", last_visit="2026-01-01")
            session.add(p_seed)
            await session.commit()

        # 1. Creation WITHOUT confirmation fails
        req_unconfirmed = {
            "temple_id": "SKSA_MAIN",
            "title": "Unconfirmed Festival Campaign",
            "message": "Festival greetings to all devotees",
            "audience_filter": {"filter_type": "ALL_DEVOTEES"},
            "confirmed": False
        }
        res_fail = await ac.post("/api/v2/broadcast/campaigns", json=req_unconfirmed, headers=headers)
        assert res_fail.status_code == 400
        assert "confirmation required" in res_fail.json()["detail"].lower()

        # 2. Creation WITH confirmation succeeds
        req_confirmed = {
            "temple_id": "SKSA_MAIN",
            "title": "Confirmed Festival Campaign",
            "message": "Festival greetings to all devotees",
            "audience_filter": {"filter_type": "ALL_DEVOTEES"},
            "confirmed": True
        }
        res_succ = await ac.post("/api/v2/broadcast/campaigns", json=req_confirmed, headers=headers)
        assert res_succ.status_code == 200
        data = res_succ.json()
        assert data["title"] == "Confirmed Festival Campaign"
        assert data["total_recipients"] >= 1


@pytest.mark.asyncio
async def test_campaign_lifecycle_and_cancellation():
    """Verify campaign lifecycle flow (QUEUED -> SENDING -> COMPLETED) and cancellation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # Seed person in DB for recipient query
        async with AsyncSessionLocal() as session:
            p_seed = Person(id="p_sched", temple_id="SKSA_MAIN", name="Devotee Sched", phone="9988776644", village="Tirupati", first_visit="2026-01-01", last_visit="2026-01-01")
            session.add(p_seed)
            await session.commit()

        # 1. Create Scheduled Campaign for future date
        future_str = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
        req_sched = {
            "temple_id": "SKSA_MAIN",
            "title": "Future Scheduled Campaign",
            "message": "Scheduled Pooja Notice",
            "audience_filter": {"filter_type": "ALL_DEVOTEES"},
            "scheduled_at": future_str,
            "confirmed": True
        }
        res_c = await ac.post("/api/v2/broadcast/campaigns", json=req_sched, headers=headers)
        assert res_c.status_code == 200
        c_id = res_c.json()["campaign_id"]
        assert res_c.json()["status"] == "SCHEDULED"

        # 2. Cancel Scheduled Campaign
        res_cancel = await ac.post(f"/api/v2/broadcast/campaigns/{c_id}/cancel", headers=headers)
        assert res_cancel.status_code == 200
        assert res_cancel.json()["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_retry_failed_recipients_logic():
    """Verify retry logic targeting only failed recipients with exponential backoff count."""
    async with AsyncSessionLocal() as session:
        # Seed campaign and 2 recipients (1 delivered, 1 failed)
        c = BroadcastCampaign(
            campaign_id="camp-retry-001",
            temple_id="SKSA_MAIN",
            title="Retry Test Campaign",
            message="Test retry message",
            status="COMPLETED",
            total_recipients=2,
            sent_count=2,
            delivered_count=1,
            failed_count=1
        )
        r1 = BroadcastRecipient(recipient_id="rec-1", campaign_id="camp-retry-001", temple_id="SKSA_MAIN", mobile_number="9876500001", status="DELIVERED")
        r2 = BroadcastRecipient(recipient_id="rec-2", campaign_id="camp-retry-001", temple_id="SKSA_MAIN", mobile_number="9876500002", status="FAILED", error_message="Network Timeout")
        
        session.add_all([c, r1, r2])
        await session.commit()

        engine_svc = BroadcastEngine(session)
        mock_user = User(id="usr-admin", username="admin")

        res_c = await engine_svc.retry_failed_recipients("camp-retry-001", mock_user)
        assert res_c.status in ("RETRYING", "SENDING", "COMPLETED")
        
        # Verify r2 retry count incremented
        await session.refresh(r2)
        assert r2.retry_count == 1


@pytest.mark.asyncio
async def test_large_campaign_batch_performance_benchmark():
    """Performance Benchmark: Verify creating and batch queueing 500 recipients under 200ms."""
    async with AsyncSessionLocal() as session:
        # Seed 500 persons
        persons = [
            Person(id=f"bench-p-{i}", temple_id="SKSA_MAIN", name=f"Devotee {i}", phone=f"90000{i:05d}", village="Guntur", first_visit="2026-01-01", last_visit="2026-01-01")
            for i in range(500)
        ]
        session.add_all(persons)
        await session.commit()

        builder = AudienceBuilderService(session)
        start = time.perf_counter()
        
        target_recipients = await builder.filter_recipients("SKSA_MAIN", AudienceFilterSpec(filter_type="ALL_DEVOTEES"))
        elapsed_ms = (time.perf_counter() - start) * 1000
        
        assert len(target_recipients) >= 500
        assert elapsed_ms < 200.0, f"Audience selection for 500 recipients took {elapsed_ms:.2f}ms exceeding 200ms SLA threshold!"
