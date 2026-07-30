from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.communication import MessageTemplate
from app.repositories.base import BaseRepository


class MessageTemplateRepository(BaseRepository[MessageTemplate]):

    def __init__(self, session: AsyncSession):
        super().__init__(MessageTemplate, session)

    async def get_by_type(self, template_type: str) -> Optional[MessageTemplate]:
        """Fetch a template by its type (ENTRY or EXIT)."""
        stmt = select(MessageTemplate).filter(
            MessageTemplate.template_type == template_type,
            MessageTemplate.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all_templates(self) -> List[MessageTemplate]:
        """Fetch all active message templates."""
        stmt = select(MessageTemplate).filter(
            MessageTemplate.is_deleted.is_(False)
        ).order_by(MessageTemplate.template_type)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def upsert_template(
        self,
        template_type: str,
        data: dict,
        user_id: Optional[str] = None,
    ) -> MessageTemplate:
        """Create or update a template by type."""
        existing = await self.get_by_type(template_type)
        if existing:
            return await self.update(existing, data, user_id=user_id)

        data["template_type"] = template_type
        return await self.create(data, user_id=user_id)
