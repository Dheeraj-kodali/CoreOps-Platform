import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone
from sqlalchemy.future import select
from app.core.database import AsyncSessionLocal
from app.models.broadcast import BroadcastCampaign
from app.models.dead_letter import DeadLetterJob
from app.core.audit_hook import record_audit_event

logger = logging.getLogger(__name__)

_HEARTBEAT_TIMESTAMP = datetime.now(timezone.utc)
_IS_SHUTTING_DOWN = False


class WorkerResilienceManager:
    """Enterprise Worker Heartbeat Monitoring, Recovery & Graceful Shutdown Service."""

    @staticmethod
    def get_last_heartbeat() -> datetime:
        return _HEARTBEAT_TIMESTAMP

    @staticmethod
    def is_shutting_down() -> bool:
        return _IS_SHUTTING_DOWN

    @staticmethod
    async def update_heartbeat():
        global _HEARTBEAT_TIMESTAMP
        _HEARTBEAT_TIMESTAMP = datetime.now(timezone.utc)

    @classmethod
    async def start_heartbeat_loop(cls, interval_seconds: int = 15):
        """Background heartbeat ticker updating worker vitality timestamp."""
        logger.info("WorkerResilienceManager: Heartbeat ticker started.")
        while not _IS_SHUTTING_DOWN:
            await cls.update_heartbeat()
            await asyncio.sleep(interval_seconds)

    @classmethod
    async def recover_stuck_broadcast_jobs(cls):
        """Finds campaigns stuck in SENDING state during crash/unexpected shutdown and safely resets them."""
        async with AsyncSessionLocal() as session:
            stmt = select(BroadcastCampaign).filter(
                BroadcastCampaign.status == "SENDING",
                BroadcastCampaign.is_deleted.is_(False),
            )
            res = await session.execute(stmt)
            stuck_campaigns = list(res.scalars().all())

            for campaign in stuck_campaigns:
                logger.warning(
                    f"WorkerResilienceManager: Recovering stuck campaign {campaign.campaign_id} '{campaign.title}'"
                )
                campaign.status = "QUEUED"
                await session.commit()

                await record_audit_event(
                    session,
                    action="STUCK_JOB_RECOVERED",
                    entity_type="BROADCAST_CAMPAIGN",
                    entity_id=campaign.campaign_id,
                    temple_id=campaign.temple_id,
                    severity="WARNING",
                    reason="Worker crashed while job was in SENDING status; automatically reset to QUEUED",
                )

                # Re-enqueue execution task
                from app.services.broadcast_engine import BroadcastEngine
                engine = BroadcastEngine(session)
                asyncio.create_task(engine.process_campaign_execution(campaign.campaign_id))

    @classmethod
    async def log_dead_letter_job(
        cls,
        job_type: str,
        entity_id: str,
        temple_id: str,
        failure_reason: str,
        stack_trace: str = None,
        payload_json: str = None,
    ) -> DeadLetterJob:
        """Records permanently failed job into Dead Letter Queue."""
        async with AsyncSessionLocal() as session:
            dl_job = DeadLetterJob(
                job_type=job_type,
                entity_id=entity_id,
                temple_id=temple_id,
                failure_reason=failure_reason,
                stack_trace=stack_trace,
                payload_json=payload_json,
                status="UNRESOLVED",
            )
            session.add(dl_job)
            await session.commit()

            logger.error(
                f"WorkerResilienceManager: Logged DeadLetterJob {dl_job.job_id} for entity {entity_id} ({failure_reason})"
            )
            return dl_job


def register_graceful_shutdown_handlers():
    """Register OS signal handlers for graceful shutdown."""
    def handle_signal(sig, frame):
        global _IS_SHUTTING_DOWN
        _IS_SHUTTING_DOWN = True
        logger.info(f"WorkerResilienceManager: Received termination signal ({sig}). Initiating graceful shutdown...")
        sys.exit(0)

    try:
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
    except (ValueError, OSError):
        # Handle non-main thread execution safely
        pass
