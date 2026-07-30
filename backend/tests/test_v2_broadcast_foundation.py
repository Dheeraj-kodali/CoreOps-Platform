import os
import pytest
import pytest_asyncio

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_temple.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test_temple.db"

from app.core.config import settings
settings.DATABASE_URL = "sqlite+aiosqlite:///./test_temple.db"
settings.SYNC_DATABASE_URL = "sqlite:///./test_temple.db"

import app.models
from app.main import seed_initial_data
from app.core.database import engine, Base, AsyncSessionLocal
from app.services.broadcast_campaign_service import BroadcastCampaignService
from app.repositories.broadcast_repository import (
    BroadcastCampaignRepository,
    BroadcastRecipientRepository,
)
from app.core.broadcast_lifecycle import (
    CampaignStatus,
    validate_campaign_state_transition,
)
from app.core.exceptions import (
    InvalidCampaignStateTransitionException,
    BroadcastValidationException,
    CampaignDeletionRestrictedException,
    DuplicateResourceException,
)
from app.models.person import Person
from app.models.audit import AuditRecord
from sqlalchemy.future import select


@pytest_asyncio.fixture(autouse=True)
async def setup_broadcast_foundation_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await seed_initial_data()
    async with AsyncSessionLocal() as session:
        # Seed test Person for audience existence validation tests
        test_person = Person(
            temple_id="SKSA_MAIN",
            name="Ramesh Kumar",
            phone="+919876543210",
            village="Kalki Nagaram",
            first_visit="2026-01-01",
            last_visit="2026-07-30",
            total_visits=1,
        )
        session.add(test_person)
        await session.commit()
    yield


@pytest.mark.asyncio
async def test_campaign_creation_and_duplicate_title_rejection():
    """Verify campaign creation in Draft status and duplicate title rejection per temple."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        # 1. Successful Campaign Creation
        campaign = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Annual Navratri Mahotsav",
            message="Join us for daily special pooja at 6:00 PM.",
            description="Navratri festival announcement",
            created_by="user_admin_01",
        )
        assert campaign.campaign_id is not None
        assert campaign.title == "Annual Navratri Mahotsav"
        assert campaign.status == CampaignStatus.DRAFT.value
        assert campaign.temple_id == "SKSA_MAIN"

        # 2. Duplicate Title Rejection
        with pytest.raises(DuplicateResourceException):
            await service.create_campaign(
                temple_id="SKSA_MAIN",
                title="Annual Navratri Mahotsav",
                message="Duplicate campaign title attempt.",
            )


@pytest.mark.asyncio
async def test_campaign_status_lifecycle_and_state_transitions():
    """Verify strict campaign state machine transitions and invalid transition exception enforcement."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        campaign = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Ugadi Special Festival",
            message="Happy Ugadi to all devotees!",
        )
        assert campaign.status == CampaignStatus.DRAFT.value

        # 1. Invalid transition: Draft -> Approved directly (must be Validated first)
        with pytest.raises(InvalidCampaignStateTransitionException):
            await service.approve_campaign(campaign.campaign_id)

        # 2. Invalid transition: Draft -> Sending directly
        with pytest.raises(InvalidCampaignStateTransitionException):
            validate_campaign_state_transition(campaign.status, CampaignStatus.SENDING.value)

        # 3. Valid transition: Draft -> Validated
        validated_campaign = await service.validate_campaign(campaign.campaign_id)
        assert validated_campaign.status == CampaignStatus.VALIDATED.value

        # 4. Valid transition: Validated -> Approved
        approved_campaign = await service.approve_campaign(campaign.campaign_id, approved_by="admin_owner")
        assert approved_campaign.status == CampaignStatus.APPROVED.value
        assert approved_campaign.approved_at is not None

        # 5. Valid transition: Approved -> Cancelled
        cancelled_campaign = await service.cancel_campaign(
            campaign.campaign_id, cancelled_by="admin_owner", reason="Schedule change"
        )
        assert cancelled_campaign.status == CampaignStatus.CANCELLED.value
        assert cancelled_campaign.cancelled_at is not None

        # 6. Terminal State: Cancelled -> Validated (Invalid)
        with pytest.raises(InvalidCampaignStateTransitionException):
            await service.validate_campaign(campaign.campaign_id)


@pytest.mark.asyncio
async def test_repository_layer_crud_operations():
    """Verify BroadcastCampaignRepository and BroadcastRecipientRepository CRUD operations."""
    async with AsyncSessionLocal() as session:
        campaign_repo = BroadcastCampaignRepository(session)
        recipient_repo = BroadcastRecipientRepository(session)

        # Campaign Repository CRUD
        campaign = await campaign_repo.create(
            {
                "temple_id": "SKSA_MAIN",
                "title": "Karthika Deepam Event",
                "message": "Special lamp lighting ceremony tomorrow.",
                "status": CampaignStatus.DRAFT.value,
            }
        )
        await session.commit()

        fetched_campaign = await campaign_repo.get_by_campaign_id(campaign.campaign_id)
        assert fetched_campaign is not None
        assert fetched_campaign.title == "Karthika Deepam Event"

        # Recipient Repository Batch CRUD
        recipients_data = [
            {
                "campaign_id": campaign.campaign_id,
                "temple_id": "SKSA_MAIN",
                "phone_number": "+919876543210",
                "status": "Queued",
            },
            {
                "campaign_id": campaign.campaign_id,
                "temple_id": "SKSA_MAIN",
                "phone_number": "+919876543211",
                "status": "Queued",
            },
        ]
        batch = await recipient_repo.create_batch(recipients_data)
        await session.commit()
        assert len(batch) == 2

        recipients = await recipient_repo.get_by_campaign(campaign.campaign_id)
        assert len(recipients) == 2

        status_counts = await recipient_repo.count_by_status(campaign.campaign_id)
        assert status_counts.get("Queued") == 2


@pytest.mark.asyncio
async def test_campaign_validation_rules_and_error_handling():
    """Verify validation rules: title non-empty, message length limits, and empty audience check."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        # 1. Invalid empty title validation
        with pytest.raises(BroadcastValidationException):
            await service.create_campaign(
                temple_id="SKSA_MAIN", title="   ", message="Valid message"
            )

        # 2. Invalid message length validation (0 length)
        with pytest.raises(BroadcastValidationException):
            await service.create_campaign(
                temple_id="SKSA_MAIN", title="Title 1", message="   "
            )

        # 3. Invalid message length validation (>4096 chars)
        with pytest.raises(BroadcastValidationException):
            await service.create_campaign(
                temple_id="SKSA_MAIN", title="Title 2", message="A" * 4097
            )

        # 4. Empty Audience Validation Failure
        # Delete test person to simulate empty audience
        await session.execute(select(Person).filter(Person.is_deleted.is_(False)))
        persons = (await session.execute(select(Person))).scalars().all()
        for p in persons:
            p.is_deleted = True
        await session.commit()

        c_empty_audience = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Empty Audience Test",
            message="Hello devotees",
        )
        with pytest.raises(BroadcastValidationException) as exc_info:
            await service.validate_campaign(c_empty_audience.campaign_id)
        assert "Audience is empty" in str(exc_info.value)


@pytest.mark.asyncio
async def test_campaign_deletion_restrictions():
    """Verify campaigns can only be deleted in Draft status; non-draft deletion is rejected."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        campaign = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Deletable Draft Campaign",
            message="Test message",
        )

        # Validate campaign -> Validated status
        validated_campaign = await service.validate_campaign(campaign.campaign_id)
        assert validated_campaign.status == CampaignStatus.VALIDATED.value

        # Attempt to delete Validated campaign -> Exception expected
        with pytest.raises(CampaignDeletionRestrictedException):
            await service.delete_draft_campaign(campaign.campaign_id)

        # Edit campaign -> reverts to Draft status
        draft_campaign = await service.update_campaign(
            campaign.campaign_id, title="Updated Deletable Draft Title"
        )
        assert draft_campaign.status == CampaignStatus.DRAFT.value

        # Delete Draft campaign -> Successful
        deleted = await service.delete_draft_campaign(campaign.campaign_id)
        assert deleted is True


@pytest.mark.asyncio
async def test_broadcast_foundation_audit_generation():
    """Verify structured audit records generated for campaign creation, update, approval, cancellation, and deletion."""
    async with AsyncSessionLocal() as session:
        service = BroadcastCampaignService(session)

        # 1. Create -> CAMPAIGN_CREATED
        campaign = await service.create_campaign(
            temple_id="SKSA_MAIN",
            title="Audit Test Campaign",
            message="Testing audit log generation",
            created_by="audit_tester_01",
        )

        # 2. Update -> CAMPAIGN_UPDATED
        await service.update_campaign(
            campaign.campaign_id,
            description="Added description",
            updated_by="audit_tester_01",
        )

        # 3. Validate & Approve -> CAMPAIGN_APPROVED
        await service.validate_campaign(campaign.campaign_id)
        await service.approve_campaign(campaign.campaign_id, approved_by="audit_approver_01")

        # 4. Cancel -> CAMPAIGN_CANCELLED
        await service.cancel_campaign(
            campaign.campaign_id, cancelled_by="audit_canceller_01", reason="Audit flow complete"
        )

        # Verify audit records in DB
        stmt = select(AuditRecord).filter(
            AuditRecord.entity_id == campaign.campaign_id
        ).order_by(AuditRecord.timestamp.asc())
        res = await session.execute(stmt)
        audits = res.scalars().all()

        actions = [a.action for a in audits]
        assert "CAMPAIGN_CREATED" in actions
        assert "CAMPAIGN_UPDATED" in actions
        assert "CAMPAIGN_APPROVED" in actions
        assert "CAMPAIGN_CANCELLED" in actions
