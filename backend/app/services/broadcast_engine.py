import uuid
import asyncio
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import AsyncSessionLocal
from app.models.broadcast import BroadcastCampaign, BroadcastRecipient
from app.models.user import User
from app.services.audience_builder import AudienceBuilderService
from app.schemas.broadcast_v2 import BroadcastCampaignCreateRequest
from app.core.audit_hook import record_audit_event


class BroadcastEngine:
    """Enterprise Execution & Queue Engine for Broadcast Campaigns v2.0."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_campaign(
        self,
        req: BroadcastCampaignCreateRequest,
        current_user: User
    ) -> BroadcastCampaign:
        # Safety Check: Require explicit user confirmation
        if not req.confirmed:
            raise ValueError("Safety rule violation: Explicit user confirmation required before campaign execution.")

        audience_service = AudienceBuilderService(self.db)
        target_persons = await audience_service.filter_recipients(req.temple_id or "SKSA_MAIN", req.audience_filter)

        if not target_persons:
            raise ValueError("Audience selection resulted in 0 recipients. Campaign cannot be created.")

        scheduled_dt: Optional[datetime] = None
        if req.scheduled_at:
            try:
                scheduled_dt = datetime.fromisoformat(req.scheduled_at.replace("Z", "+00:00"))
            except ValueError:
                scheduled_dt = None

        initial_status = "SCHEDULED" if (scheduled_dt and scheduled_dt > datetime.now(timezone.utc)) else "QUEUED"

        campaign = BroadcastCampaign(
            campaign_id=str(uuid.uuid4()),
            temple_id=req.temple_id or "SKSA_MAIN",
            title=req.title,
            description=req.description,
            template_id=req.template_id,
            message=req.message,
            status=initial_status,
            created_by=current_user.id,
            created_at=datetime.now(timezone.utc),
            scheduled_at=scheduled_dt,
            total_recipients=len(target_persons),
            queued_count=len(target_persons),
            audience_filter_json=req.audience_filter.model_dump_json(),
        )

        self.db.add(campaign)
        await self.db.flush()

        # Batch insert recipients
        recipients_list = [
            BroadcastRecipient(
                recipient_id=str(uuid.uuid4()),
                campaign_id=campaign.campaign_id,
                temple_id=campaign.temple_id,
                person_uuid=p.id,
                mobile_number=p.mobile_number,
                name=p.name,
                status="QUEUED"
            )
            for p in target_persons
        ]

        self.db.add_all(recipients_list)
        await self.db.commit()
        await self.db.refresh(campaign)

        # Audit Event
        audit_action = "CAMPAIGN_SCHEDULED" if initial_status == "SCHEDULED" else "CAMPAIGN_CREATED"
        await record_audit_event(
            self.db,
            action=audit_action,
            entity_type="BROADCAST",
            entity_id=campaign.campaign_id,
            user_id=current_user.id,
            temple_id=campaign.temple_id,
            severity="INFO",
            new_value={"title": campaign.title, "total_recipients": campaign.total_recipients, "status": initial_status}
        )

        # Trigger Immediate Background Processing if QUEUED
        if initial_status == "QUEUED":
            asyncio.create_task(self.process_campaign_execution(campaign.campaign_id))

        return campaign

    async def process_campaign_execution(self, campaign_id: str, batch_size: int = 50):
        """Asynchronous background batch processing engine for broadcast campaigns with independent session lifecycle."""
        async with AsyncSessionLocal() as session:
            # Query campaign
            q = select(BroadcastCampaign).filter(BroadcastCampaign.campaign_id == campaign_id)
            res = await session.execute(q)
            campaign = res.scalars().first()

            if not campaign or campaign.status in ("CANCELLED", "COMPLETED"):
                return

            # Double-execution protection
            if campaign.status == "SENDING":
                return

            campaign.status = "SENDING"
            campaign.started_at = datetime.now(timezone.utc)
            await session.commit()

            # Audit Event
            await record_audit_event(
                session,
                action="CAMPAIGN_STARTED",
                entity_type="BROADCAST",
                entity_id=campaign.campaign_id,
                temple_id=campaign.temple_id,
                severity="INFO"
            )

            # Fetch QUEUED recipients in batches
            q_rec = select(BroadcastRecipient).filter(
                BroadcastRecipient.campaign_id == campaign_id,
                BroadcastRecipient.status == "QUEUED"
            )
            res_rec = await session.execute(q_rec)
            queued_recipients = list(res_rec.scalars().all())

            sent_delta = 0
            delivered_delta = 0
            failed_delta = 0

            # Process in batches to satisfy Meta API rate limits and non-blocking performance SLA
            for i in range(0, len(queued_recipients), batch_size):
                batch = queued_recipients[i:i + batch_size]
                
                for rec in batch:
                    # Re-verify campaign cancellation status
                    if campaign.status == "CANCELLED":
                        rec.status = "CANCELLED"
                        continue

                    now_ts = datetime.now(timezone.utc)
                    # Mock Meta WhatsApp API Delivery Dispatch
                    if rec.mobile_number and len(rec.mobile_number) >= 5:
                        rec.status = "DELIVERED"
                        rec.sent_at = now_ts
                        rec.delivered_at = now_ts
                        sent_delta += 1
                        delivered_delta += 1
                    else:
                        rec.status = "FAILED"
                        rec.failed_at = now_ts
                        rec.error_message = "Invalid mobile number formatting"
                        failed_delta += 1
                        
                        # Audit Failure
                        await record_audit_event(
                            session,
                            action="DELIVERY_FAILURE",
                            entity_type="BROADCAST_RECIPIENT",
                            entity_id=rec.recipient_id,
                            temple_id=campaign.temple_id,
                            severity="WARNING",
                            new_value={"mobile_number": rec.mobile_number, "reason": rec.error_message}
                        )

                # Update Campaign Counts
                campaign.queued_count = max(0, campaign.queued_count - len(batch))
                campaign.sent_count += sent_delta
                campaign.delivered_count += delivered_delta
                campaign.failed_count += failed_delta
                
                await session.commit()
                await asyncio.sleep(0.01)  # Non-blocking async sleep yield

            campaign.status = "COMPLETED"
            campaign.completed_at = datetime.now(timezone.utc)
            await session.commit()

            # Audit Event
            await record_audit_event(
                session,
                action="CAMPAIGN_COMPLETED",
                entity_type="BROADCAST",
                entity_id=campaign.campaign_id,
                temple_id=campaign.temple_id,
                severity="INFO",
                new_value={
                    "delivered_count": campaign.delivered_count,
                    "failed_count": campaign.failed_count,
                    "total_recipients": campaign.total_recipients
                }
            )

    async def cancel_campaign(self, campaign_id: str, current_user: User) -> BroadcastCampaign:
        q = select(BroadcastCampaign).filter(BroadcastCampaign.campaign_id == campaign_id)
        res = await self.db.execute(q)
        campaign = res.scalars().first()

        if not campaign:
            raise ValueError("Campaign not found")

        if campaign.status in ("COMPLETED", "CANCELLED"):
            return campaign

        campaign.status = "CANCELLED"
        await self.db.commit()

        # Audit Event
        await record_audit_event(
            self.db,
            action="CAMPAIGN_CANCELLED",
            entity_type="BROADCAST",
            entity_id=campaign.campaign_id,
            user_id=current_user.id,
            temple_id=campaign.temple_id,
            severity="WARNING"
        )
        return campaign

    async def retry_failed_recipients(self, campaign_id: str, current_user: User) -> BroadcastCampaign:
        q = select(BroadcastCampaign).filter(BroadcastCampaign.campaign_id == campaign_id)
        res = await self.db.execute(q)
        campaign = res.scalars().first()

        if not campaign:
            raise ValueError("Campaign not found")

        q_failed = select(BroadcastRecipient).filter(
            BroadcastRecipient.campaign_id == campaign_id,
            BroadcastRecipient.status == "FAILED"
        )
        res_failed = await self.db.execute(q_failed)
        failed_recipients = list(res_failed.scalars().all())

        if not failed_recipients:
            return campaign

        campaign.status = "RETRYING"
        for rec in failed_recipients:
            rec.status = "QUEUED"
            rec.retry_count += 1
            campaign.failed_count = max(0, campaign.failed_count - 1)
            campaign.queued_count += 1

        await self.db.commit()

        # Audit Event
        await record_audit_event(
            self.db,
            action="RECIPIENT_RETRY",
            entity_type="BROADCAST",
            entity_id=campaign.campaign_id,
            user_id=current_user.id,
            temple_id=campaign.temple_id,
            severity="INFO",
            new_value={"retried_recipients_count": len(failed_recipients)}
        )

        asyncio.create_task(self.process_campaign_execution(campaign.campaign_id))
        return campaign
