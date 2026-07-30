from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.broadcast import BroadcastCampaign
from app.models.person import Person
from app.repositories.broadcast_repository import (
    BroadcastCampaignRepository,
    BroadcastRecipientRepository,
)
from app.core.broadcast_lifecycle import (
    CampaignStatus,
    validate_campaign_state_transition,
)
from app.core.exceptions import (
    CampaignNotFoundException,
    DuplicateResourceException,
    BroadcastValidationException,
    CampaignDeletionRestrictedException,
)
from app.core.audit_hook import record_audit_event


class BroadcastCampaignService:
    """Service layer foundation for managing Broadcast Campaign lifecycle, validation, and audit events.
    
    Contains pure domain infrastructure without sending actual WhatsApp messages or executing background workers.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.campaign_repo = BroadcastCampaignRepository(db)
        self.recipient_repo = BroadcastRecipientRepository(db)

    async def create_campaign(
        self,
        temple_id: str,
        title: str,
        message: str,
        description: Optional[str] = None,
        template_id: Optional[str] = None,
        audience_filter_json: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> BroadcastCampaign:
        """Creates a new Broadcast Campaign in Draft status."""
        title_clean = title.strip()
        if not title_clean:
            raise BroadcastValidationException("Campaign title cannot be empty.")
        
        if len(message.strip()) == 0 or len(message) > 4096:
            raise BroadcastValidationException("Campaign message must be between 1 and 4096 characters.")

        # Duplicate campaign name check per temple
        existing = await self.campaign_repo.get_by_title_and_temple(title_clean, temple_id)
        if existing:
            raise DuplicateResourceException(f"Campaign with title '{title_clean}' already exists for this temple.")

        campaign_data = {
            "temple_id": temple_id,
            "title": title_clean,
            "description": description,
            "template_id": template_id,
            "message": message,
            "status": CampaignStatus.DRAFT.value,
            "audience_filter_json": audience_filter_json,
            "created_by": created_by,
        }

        campaign = await self.campaign_repo.create(campaign_data, user_id=created_by)
        await self.db.commit()

        # Audit Integration: Campaign Created
        await record_audit_event(
            self.db,
            action="CAMPAIGN_CREATED",
            resource="broadcast_campaign",
            user_id=created_by,
            temple_id=temple_id,
            entity_type="BROADCAST_CAMPAIGN",
            entity_id=campaign.campaign_id,
            new_value={"title": campaign.title, "status": campaign.status},
            result="SUCCESS",
        )

        return campaign

    async def update_campaign(
        self,
        campaign_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        message: Optional[str] = None,
        template_id: Optional[str] = None,
        audience_filter_json: Optional[str] = None,
        updated_by: Optional[str] = None,
    ) -> BroadcastCampaign:
        """Updates a campaign if it is in Draft or Validated status."""
        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        if campaign.status not in (CampaignStatus.DRAFT.value, CampaignStatus.VALIDATED.value):
            raise BroadcastValidationException(
                f"Campaign in '{campaign.status}' status cannot be updated. Only Draft or Validated campaigns can be modified."
            )

        old_values = {"title": campaign.title, "message": campaign.message, "status": campaign.status}
        update_dict: Dict[str, Any] = {}

        if title is not None:
            title_clean = title.strip()
            if not title_clean:
                raise BroadcastValidationException("Campaign title cannot be empty.")
            if title_clean.lower() != campaign.title.lower():
                existing = await self.campaign_repo.get_by_title_and_temple(title_clean, campaign.temple_id)
                if existing and existing.campaign_id != campaign.campaign_id:
                    raise DuplicateResourceException(f"Campaign with title '{title_clean}' already exists.")
            update_dict["title"] = title_clean

        if message is not None:
            if len(message.strip()) == 0 or len(message) > 4096:
                raise BroadcastValidationException("Campaign message must be between 1 and 4096 characters.")
            update_dict["message"] = message

        if description is not None:
            update_dict["description"] = description
        if template_id is not None:
            update_dict["template_id"] = template_id
        if audience_filter_json is not None:
            update_dict["audience_filter_json"] = audience_filter_json

        # If campaign was Validated, editing moves it back to Draft for re-validation
        if campaign.status == CampaignStatus.VALIDATED.value:
            validate_campaign_state_transition(campaign.status, CampaignStatus.DRAFT.value)
            update_dict["status"] = CampaignStatus.DRAFT.value

        updated_campaign = await self.campaign_repo.update(campaign, update_dict, user_id=updated_by)
        await self.db.commit()

        # Audit Integration: Campaign Updated
        await record_audit_event(
            self.db,
            action="CAMPAIGN_UPDATED",
            resource="broadcast_campaign",
            user_id=updated_by,
            temple_id=campaign.temple_id,
            entity_type="BROADCAST_CAMPAIGN",
            entity_id=campaign.campaign_id,
            old_value=old_values,
            new_value=update_dict,
            result="SUCCESS",
        )

        return updated_campaign

    async def delete_draft_campaign(self, campaign_id: str, deleted_by: Optional[str] = None) -> bool:
        """Deletes a campaign only if its status is Draft."""
        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        if campaign.status != CampaignStatus.DRAFT.value:
            raise CampaignDeletionRestrictedException(
                f"Cannot delete campaign in '{campaign.status}' status. Only Draft campaigns can be deleted."
            )

        success = await self.campaign_repo.soft_delete(campaign.campaign_id, user_id=deleted_by)
        await self.db.commit()

        if success:
            await record_audit_event(
                self.db,
                action="CAMPAIGN_DELETED",
                resource="broadcast_campaign",
                user_id=deleted_by,
                temple_id=campaign.temple_id,
                entity_type="BROADCAST_CAMPAIGN",
                entity_id=campaign.campaign_id,
                old_value={"title": campaign.title, "status": campaign.status},
                result="SUCCESS",
            )
        return success

    async def validate_campaign(self, campaign_id: str) -> BroadcastCampaign:
        """Validates campaign requirements (title, message length, audience existence) and transitions Draft -> Validated."""
        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        # 1. Validate Campaign Title
        if not campaign.title or len(campaign.title.strip()) == 0:
            err_msg = "Validation failed: Campaign title is missing or empty."
            await self._audit_validation_failed(campaign, err_msg)
            raise BroadcastValidationException(err_msg)

        # 2. Validate Message Length
        if not campaign.message or len(campaign.message.strip()) == 0 or len(campaign.message) > 4096:
            err_msg = "Validation failed: Message content must be between 1 and 4096 characters."
            await self._audit_validation_failed(campaign, err_msg)
            raise BroadcastValidationException(err_msg)

        # 3. Validate Audience Existence (> 0 recipients)
        person_count_stmt = select(func.count(Person.id)).filter(Person.is_deleted.is_(False))
        res = await self.db.execute(person_count_stmt)
        recipient_count = res.scalar_one()

        if recipient_count == 0:
            err_msg = "Validation failed: Audience is empty. At least 1 recipient is required."
            await self._audit_validation_failed(campaign, err_msg)
            raise BroadcastValidationException(err_msg)

        # 4. State Transition: Draft -> Validated
        validate_campaign_state_transition(campaign.status, CampaignStatus.VALIDATED.value)
        campaign.status = CampaignStatus.VALIDATED.value
        campaign.estimated_recipients = recipient_count
        self.db.add(campaign)
        await self.db.commit()

        return campaign

    async def approve_campaign(
        self, campaign_id: str, approved_by: Optional[str] = None
    ) -> BroadcastCampaign:
        """Approves a Validated campaign, transitioning Validated -> Approved and freezing recipient snapshot."""
        import json
        import uuid
        from app.schemas.broadcast_v2 import AudienceFilterSpec
        from app.services.audience_builder import AudienceBuilderService
        from app.models.broadcast import BroadcastRecipient

        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        validate_campaign_state_transition(campaign.status, CampaignStatus.APPROVED.value)

        # Freeze Audience Snapshot into BroadcastRecipient records
        spec = AudienceFilterSpec(filter_type="ALL_DEVOTEES")
        if campaign.audience_filter_json:
            try:
                filter_dict = json.loads(campaign.audience_filter_json)
                spec = AudienceFilterSpec(**filter_dict)
            except Exception:
                pass

        builder = AudienceBuilderService(self.db)
        target_persons = await builder.filter_recipients(campaign.temple_id, spec)

        # Check existing frozen recipients
        existing_recs = await self.recipient_repo.get_by_campaign(campaign.campaign_id)
        if not existing_recs and target_persons:
            frozen_recipients = [
                BroadcastRecipient(
                    recipient_id=str(uuid.uuid4()),
                    campaign_id=campaign.campaign_id,
                    temple_id=campaign.temple_id,
                    person_id=p.id,
                    person_uuid=p.id,
                    phone_number=getattr(p, "phone", None) or getattr(p, "mobile_number", None) or "",
                    mobile_number=getattr(p, "phone", None) or getattr(p, "mobile_number", None) or "",
                    name=p.name,
                    status="Queued",
                    queued_at=datetime.now(timezone.utc),
                )
                for p in target_persons
            ]
            self.db.add_all(frozen_recipients)

        count = len(target_persons) if target_persons else len(existing_recs)
        campaign.status = CampaignStatus.APPROVED.value
        campaign.approved_at = datetime.now(timezone.utc)
        campaign.total_recipients = count
        campaign.estimated_recipients = count
        campaign.queued_count = count

        self.db.add(campaign)
        await self.db.commit()

        # Audit Integration: Campaign Approved
        await record_audit_event(
            self.db,
            action="CAMPAIGN_APPROVED",
            resource="broadcast_campaign",
            user_id=approved_by,
            temple_id=campaign.temple_id,
            entity_type="BROADCAST_CAMPAIGN",
            entity_id=campaign.campaign_id,
            new_value={"approved_at": campaign.approved_at.isoformat(), "status": campaign.status, "frozen_recipients_count": count},
            result="SUCCESS",
        )

        return campaign

    async def cancel_campaign(
        self, campaign_id: str, cancelled_by: Optional[str] = None, reason: Optional[str] = None
    ) -> BroadcastCampaign:
        """Cancels an active campaign, transitioning status -> Cancelled."""
        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        validate_campaign_state_transition(campaign.status, CampaignStatus.CANCELLED.value)

        old_status = campaign.status
        campaign.status = CampaignStatus.CANCELLED.value
        campaign.cancelled_at = datetime.now(timezone.utc)
        self.db.add(campaign)
        await self.db.commit()

        # Audit Integration: Campaign Cancelled
        await record_audit_event(
            self.db,
            action="CAMPAIGN_CANCELLED",
            resource="broadcast_campaign",
            user_id=cancelled_by,
            temple_id=campaign.temple_id,
            entity_type="BROADCAST_CAMPAIGN",
            entity_id=campaign.campaign_id,
            old_value={"status": old_status},
            new_value={"cancelled_at": campaign.cancelled_at.isoformat(), "reason": reason},
            result="SUCCESS",
        )

        return campaign

    async def get_campaign_statistics(self, campaign_id: str) -> Dict[str, Any]:
        """Returns campaign statistics and recipient metrics."""
        campaign = await self.campaign_repo.get_by_campaign_id(campaign_id)
        if not campaign:
            raise CampaignNotFoundException(campaign_id)

        return await self.campaign_repo.get_campaign_stats(campaign_id)

    async def _audit_validation_failed(self, campaign: BroadcastCampaign, reason: str):
        """Helper to emit CAMPAIGN_VALIDATION_FAILED audit log."""
        await record_audit_event(
            self.db,
            action="CAMPAIGN_VALIDATION_FAILED",
            resource="broadcast_campaign",
            temple_id=campaign.temple_id,
            entity_type="BROADCAST_CAMPAIGN",
            entity_id=campaign.campaign_id,
            reason=reason,
            result="FAILURE",
        )
