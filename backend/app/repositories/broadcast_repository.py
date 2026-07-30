from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.broadcast import BroadcastCampaign, BroadcastRecipient
from app.repositories.base import BaseRepository


class BroadcastCampaignRepository(BaseRepository[BroadcastCampaign]):
    def __init__(self, session: AsyncSession):
        super().__init__(BroadcastCampaign, session)

    async def get_by_campaign_id(self, campaign_id: str) -> Optional[BroadcastCampaign]:
        stmt = select(BroadcastCampaign).filter(
            BroadcastCampaign.campaign_id == str(campaign_id),
            BroadcastCampaign.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_title_and_temple(
        self, title: str, temple_id: str
    ) -> Optional[BroadcastCampaign]:
        stmt = select(BroadcastCampaign).filter(
            func.lower(BroadcastCampaign.title) == title.strip().lower(),
            BroadcastCampaign.temple_id == temple_id,
            BroadcastCampaign.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_temple(
        self, temple_id: str, skip: int = 0, limit: int = 100
    ) -> List[BroadcastCampaign]:
        stmt = (
            select(BroadcastCampaign)
            .filter(
                BroadcastCampaign.temple_id == temple_id,
                BroadcastCampaign.is_deleted.is_(False),
            )
            .order_by(BroadcastCampaign.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update_status(
        self, campaign_id: str, new_status: str, timestamps: Optional[Dict[str, Any]] = None
    ) -> Optional[BroadcastCampaign]:
        campaign = await self.get_by_campaign_id(campaign_id)
        if not campaign:
            return None
        campaign.status = new_status
        if timestamps:
            for field, val in timestamps.items():
                if hasattr(campaign, field):
                    setattr(campaign, field, val)
        self.session.add(campaign)
        await self.session.flush()
        return campaign

    async def soft_delete(self, id: Any, user_id: Optional[str] = None) -> bool:
        from datetime import datetime, timezone
        db_obj = await self.get_by_campaign_id(str(id))
        if db_obj:
            db_obj.is_deleted = True
            db_obj.deleted_at = datetime.now(timezone.utc)
            if user_id:
                db_obj.updated_by = user_id
            self.session.add(db_obj)
            await self.session.flush()
            return True
        return False

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        campaign = await self.get_by_campaign_id(campaign_id)
        if not campaign:
            return {}
        return {
            "campaign_id": campaign.campaign_id,
            "status": campaign.status,
            "estimated_recipients": campaign.estimated_recipients,
            "actual_recipients": campaign.actual_recipients,
            "queued_count": campaign.queued_count,
            "sent_count": campaign.sent_count,
            "delivered_count": campaign.delivered_count,
            "failed_count": campaign.failed_count,
            "retry_count": campaign.retry_count,
        }


class BroadcastRecipientRepository(BaseRepository[BroadcastRecipient]):
    def __init__(self, session: AsyncSession):
        super().__init__(BroadcastRecipient, session)

    async def create_batch(
        self, recipients_data: List[Dict[str, Any]]
    ) -> List[BroadcastRecipient]:
        db_objs = [BroadcastRecipient(**item) for item in recipients_data]
        self.session.add_all(db_objs)
        await self.session.flush()
        return db_objs

    async def get_by_campaign(
        self, campaign_id: str, skip: int = 0, limit: int = 100
    ) -> List[BroadcastRecipient]:
        stmt = (
            select(BroadcastRecipient)
            .filter(
                BroadcastRecipient.campaign_id == str(campaign_id),
                BroadcastRecipient.is_deleted.is_(False),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_by_status(self, campaign_id: str) -> Dict[str, int]:
        stmt = (
            select(BroadcastRecipient.status, func.count(BroadcastRecipient.recipient_id))
            .filter(
                BroadcastRecipient.campaign_id == str(campaign_id),
                BroadcastRecipient.is_deleted.is_(False),
            )
            .group_by(BroadcastRecipient.status)
        )
        result = await self.session.execute(stmt)
        return {status_val: count for status_val, count in result.all()}
