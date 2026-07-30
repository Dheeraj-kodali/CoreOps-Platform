import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.broadcast import BroadcastCampaign
from app.core.audit_hook import record_audit_event

logger = logging.getLogger(__name__)

_SCHEDULER_RUNNING = False


async def check_and_trigger_scheduled_campaigns():
    """Poll for due scheduled broadcast campaigns and enqueue them for execution."""
    async with AsyncSessionLocal() as session:
        now_ts = datetime.now(timezone.utc)
        stmt = (
            select(BroadcastCampaign)
            .filter(
                BroadcastCampaign.status == "SCHEDULED",
                BroadcastCampaign.scheduled_at <= now_ts,
                BroadcastCampaign.is_deleted.is_(False),
            )
        )
        res = await session.execute(stmt)
        due_campaigns = list(res.scalars().all())

        for campaign in due_campaigns:
            logger.info(f"BroadcastScheduler: Triggering scheduled campaign {campaign.campaign_id} '{campaign.title}'")
            campaign.status = "QUEUED"
            await session.commit()

            # Record Audit Event
            await record_audit_event(
                session,
                action="SCHEDULED_CAMPAIGN_TRIGGERED",
                entity_type="BROADCAST",
                entity_id=campaign.campaign_id,
                temple_id=campaign.temple_id,
                severity="INFO",
                new_value={"scheduled_at": campaign.scheduled_at.isoformat() if campaign.scheduled_at else None},
            )

            # Lazy import to avoid circular dependency
            from app.services.broadcast_engine import BroadcastEngine
            engine = BroadcastEngine(session)
            asyncio.create_task(engine.process_campaign_execution(campaign.campaign_id))


async def start_broadcast_scheduler_loop(poll_interval_seconds: int = 30):
    """Background polling loop for scheduled broadcast execution."""
    global _SCHEDULER_RUNNING
    if _SCHEDULER_RUNNING:
        return
    _SCHEDULER_RUNNING = True
    logger.info("BroadcastScheduler: Background polling loop started.")
    try:
        while _SCHEDULER_RUNNING:
            try:
                await check_and_trigger_scheduled_campaigns()
            except Exception as e:
                logger.error(f"BroadcastScheduler: Error checking scheduled campaigns: {e}", exc_info=True)
            await asyncio.sleep(poll_interval_seconds)
    finally:
        _SCHEDULER_RUNNING = False
