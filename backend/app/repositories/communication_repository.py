from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.communication import CommunicationSetting
from app.repositories.base import BaseRepository


class CommunicationRepository(BaseRepository[CommunicationSetting]):

    def __init__(self, session: AsyncSession):
        super().__init__(CommunicationSetting, session)

    async def get_settings(self) -> Optional[CommunicationSetting]:
        """Return the singleton communication settings row."""
        stmt = select(CommunicationSetting).filter(
            CommunicationSetting.is_deleted.is_(False)
        ).limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_or_create_settings(self) -> CommunicationSetting:
        """Return existing settings or create a default row."""
        existing = await self.get_settings()
        if existing:
            return existing

        defaults = {
            "mode": "N8N_AUTOMATION",
            "access_token": None,
            "phone_number_id": None,
            "business_account_id": None,
            "verify_token": None,
            "n8n_webhook_url": "https://n8n.kalkiseva.org/webhook/whatsapp-send",
            "auto_send": True,
            "allow_edit": False,
            "save_history": True,
            "retry_failed": False,
        }
        return await self.create(defaults)

    async def update_settings(
        self, data: dict, user_id: Optional[str] = None
    ) -> CommunicationSetting:
        """Upsert communication settings — creates if none exists, updates otherwise."""
        settings = await self.get_or_create_settings()
        return await self.update(settings, data, user_id=user_id)
