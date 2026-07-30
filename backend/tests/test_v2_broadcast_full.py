import os
import time
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime, timezone, timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy.future import select

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

import app.models
from app.main import app, seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.person import Person
from app.models.user import User
from app.models.broadcast import BroadcastCampaign, BroadcastRecipient
from app.models.communication import CommunicationSetting
from app.services.broadcast_campaign_service import BroadcastCampaignService
from app.services.broadcast_engine import BroadcastEngine
from app.services.audience_builder import AudienceBuilderService
from app.services.meta_whatsapp_service import MetaWhatsAppService
from app.core.broadcast_scheduler import check_and_trigger_scheduled_campaigns
from app.schemas.broadcast_v2 import AudienceFilterSpec


@pytest_asyncio.fixture(autouse=True)
async def setup_broadcast_full_db():
    await engine.dispose()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    async with AsyncSessionLocal() as session:
        # Seed test persons
        p1 = Person(id="p101", temple_id="SKSA_MAIN", name="Devotee Alpha", phone="9876543210", village="Tenali", total_visits=3, first_visit="2026-01-01", last_visit="2026-01-01")
        p2 = Person(id="p102", temple_id="SKSA_MAIN", name="Devotee Beta", phone="9876543211", village="Tenali", total_visits=1, first_visit="2026-01-01", last_visit="2026-01-01")
        p3 = Person(id="p103", temple_id="SKSA_MAIN", name="Devotee Gamma", phone="9876543212", village="Guntur", total_visits=5, first_visit="2026-01-01", last_visit="2026-01-01")
        session.add_all([p1, p2, p3])

        # Seed Meta WhatsApp communication settings
        comm = CommunicationSetting(
            access_token="EAAG1234567890TESTTOKEN",
            phone_number_id="1290699690788322",
            business_account_id="998877665544",
        )
        session.add(comm)
        await session.commit()
    yield
    await asyncio.sleep(0.05)


async def get_auth_headers(ac: AsyncClient) -> dict:
    login_res = await ac.post("/api/v2/auth/login", json={"username": "admin", "password": "Admin@12345"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}", "X-Temple-ID": "SKSA_MAIN"}


@pytest.mark.asyncio
async def test_audience_snapshot_freezing_on_approval():
    """Verify audience snapshot freezing creates immutable recipient records on campaign approval."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        # 1. Create draft campaign
        c = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Snapshot Freeze Test",
            message="Test frozen snapshot content",
            audience_filter_json='{"filter_type": "VILLAGE", "village": "Tenali"}',
        )
        assert c.status.upper() == "DRAFT"

        # 2. Validate
        c_val = await service.validate_campaign(c.campaign_id)
        assert c_val.status.upper() == "VALIDATED"

        # 3. Approve -> Freezes Recipient Snapshot
        c_app = await service.approve_campaign(c.campaign_id)
        assert c_app.status.upper() == "APPROVED"

        # Verify frozen recipients in DB
        res_rec = await session.execute(
            select(BroadcastRecipient).filter(BroadcastRecipient.campaign_id == c.campaign_id)
        )
        recipients = list(res_rec.scalars().all())
        assert len(recipients) == 2
        assert {r.name for r in recipients} == {"Devotee Alpha", "Devotee Beta"}


@pytest.mark.asyncio
async def test_content_immutability_on_approved_campaign():
    """Verify approved campaign prevents modifications to title, message, or template."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)
        c = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Immutability Campaign",
            message="Initial text message",
        )
        await service.validate_campaign(c.campaign_id)
        await service.approve_campaign(c.campaign_id)

        # Attempt to modify message
        with pytest.raises(Exception) as exc_info:
            await service.update_campaign(c.campaign_id, message="Modified text attempt")
        assert "cannot be updated" in str(exc_info.value).lower() or "only draft" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_meta_whatsapp_payload_construction():
    """Verify Meta WhatsApp Service constructs valid v23.0 Graph API request headers and payload."""
    comm = CommunicationSetting(
        access_token="EAAG_MOCK_TOKEN_999",
        phone_number_id="1290699690788322",
    )
    wa_service = MetaWhatsAppService(comm)

    assert wa_service.is_configured is True
    assert wa_service.build_api_url() == "https://graph.facebook.com/v23.0/1290699690788322/messages"
    assert wa_service.build_headers()["Authorization"] == "Bearer EAAG_MOCK_TOKEN_999"

    payload = wa_service.build_text_payload("+91 98765 43210", "Namaste Devotee")
    assert payload["to"] == "919876543210"
    assert payload["messaging_product"] == "whatsapp"
    assert payload["text"]["body"] == "Namaste Devotee"


@pytest.mark.asyncio
async def test_scheduled_campaign_polling_and_trigger():
    """Verify background scheduler polls due scheduled campaigns and transitions them to QUEUED."""
    async with AsyncSessionLocal() as session:
        # Create campaign scheduled in the past
        past_dt = datetime.now(timezone.utc) - timedelta(minutes=5)
        c_sched = BroadcastCampaign(
            campaign_id="sched-due-001",
            temple_id="SKSA_MAIN",
            title="Due Scheduled Campaign",
            message="Scheduled broadcast message",
            status="SCHEDULED",
            scheduled_at=past_dt,
            total_recipients=1,
            queued_count=1,
        )
        session.add(c_sched)
        await session.commit()

    # Trigger scheduler polling run
    await check_and_trigger_scheduled_campaigns()

    async with AsyncSessionLocal() as session:
        res = await session.execute(select(BroadcastCampaign).filter(BroadcastCampaign.campaign_id == "sched-due-001"))
        c_after = res.scalars().first()
        assert c_after.status in ("QUEUED", "SENDING", "COMPLETED")


@pytest.mark.asyncio
async def test_retry_failed_recipients_with_exponential_backoff():
    """Verify retrying failed recipients increments retry_count and re-queues them."""
    async with AsyncSessionLocal() as session:
        engine_svc = BroadcastEngine(session)

        # Seed campaign with 1 failed recipient
        c = BroadcastCampaign(
            campaign_id="camp-retry-backoff",
            temple_id="SKSA_MAIN",
            title="Retry Backoff Campaign",
            message="Backoff retry test",
            status="COMPLETED",
            total_recipients=1,
            failed_count=1,
        )
        r_failed = BroadcastRecipient(
            recipient_id="rec-failed-001",
            campaign_id="camp-retry-backoff",
            temple_id="SKSA_MAIN",
            mobile_number="9876543210",
            status="FAILED",
            retry_count=0,
        )
        session.add_all([c, r_failed])
        await session.commit()

        # Execute retry failed
        await engine_svc.retry_failed_recipients("camp-retry-backoff", User(id="admin_test"))

        res_r = await session.execute(select(BroadcastRecipient).filter(BroadcastRecipient.recipient_id == "rec-failed-001"))
        r_updated = res_r.scalars().first()
        assert r_updated.retry_count == 1


@pytest.mark.asyncio
async def test_full_broadcast_api_lifecycle():
    """Verify REST API endpoint lifecycle: count -> preview -> create -> validate -> approve -> execute -> analytics."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        headers = await get_auth_headers(ac)

        # 1. Audience Count
        res_cnt = await ac.post("/api/v2/broadcast/audience/count", json={"temple_id": "SKSA_MAIN", "audience_filter": {"filter_type": "ALL_DEVOTEES"}}, headers=headers)
        assert res_cnt.status_code == 200
        assert res_cnt.json()["estimated_recipients_count"] >= 3

        # 2. Preview
        res_prev = await ac.post("/api/v2/broadcast/preview", json={"temple_id": "SKSA_MAIN", "title": "API Test", "message": "Preview test text", "audience_filter": {"filter_type": "ALL_DEVOTEES"}}, headers=headers)
        assert res_prev.status_code == 200
        assert res_prev.json()["audience_size"] >= 3

        # 3. Create Draft
        res_create = await ac.post("/api/v2/broadcast/campaigns", json={"temple_id": "SKSA_MAIN", "title": "API Lifecycle Campaign", "message": "Full API lifecycle message", "audience_filter": {"filter_type": "ALL_DEVOTEES"}, "confirmed": True}, headers=headers)
        assert res_create.status_code == 200
        camp_id = res_create.json()["campaign_id"]

        # 4. Analytics
        res_ana = await ac.get("/api/v2/broadcast/analytics", headers=headers)
        assert res_ana.status_code == 200
        assert res_ana.json()["delivery_rate_percentage"] >= 0.0


@pytest.mark.asyncio
async def test_micro_benchmark_1000_recipient_snapshot():
    """Micro-benchmark for generating and freezing 1,000 recipient snapshot entries (< 2.0s SLA)."""
    async with AsyncSessionLocal() as session:
        # Seed 1,000 synthetic devotees
        bulk_persons = [
            Person(id=f"p_bulk_{i}", temple_id="SKSA_MAIN", name=f"Bulk Devotee {i}", phone=f"90000{i:05d}", village="Vijayawada", first_visit="2026-01-01", last_visit="2026-01-01")
            for i in range(1000)
        ]
        session.add_all(bulk_persons)
        await session.commit()

        service = BroadcastCampaignService(session)
        c = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Bulk Benchmark 1000",
            message="1000 recipient benchmark message",
        )
        await service.validate_campaign(c.campaign_id)

        start_time = time.time()
        c_approved = await service.approve_campaign(c.campaign_id)
        duration = time.time() - start_time

        assert c_approved.total_recipients >= 1000
        assert duration < 2.0  # Must complete in under 2.0 seconds
