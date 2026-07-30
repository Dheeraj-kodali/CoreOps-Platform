from enum import Enum
from typing import Set, Dict


class CampaignStatus(str, Enum):
    DRAFT = "Draft"
    VALIDATED = "Validated"
    APPROVED = "Approved"
    QUEUED = "Queued"
    SENDING = "Sending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    FAILED = "Failed"
    PARTIALLY_COMPLETED = "PartiallyCompleted"


# Defined valid state transition map for campaign lifecycle
VALID_STATE_TRANSITIONS: Dict[str, Set[str]] = {
    CampaignStatus.DRAFT.value: {
        CampaignStatus.VALIDATED.value,
        CampaignStatus.CANCELLED.value,
    },
    CampaignStatus.VALIDATED.value: {
        CampaignStatus.APPROVED.value,
        CampaignStatus.DRAFT.value,
        CampaignStatus.CANCELLED.value,
    },
    CampaignStatus.APPROVED.value: {
        CampaignStatus.QUEUED.value,
        CampaignStatus.CANCELLED.value,
    },
    CampaignStatus.QUEUED.value: {
        CampaignStatus.SENDING.value,
        CampaignStatus.CANCELLED.value,
    },
    CampaignStatus.SENDING.value: {
        CampaignStatus.COMPLETED.value,
        CampaignStatus.PARTIALLY_COMPLETED.value,
        CampaignStatus.FAILED.value,
        CampaignStatus.CANCELLED.value,
    },
    # Terminal states have no valid outgoing transitions
    CampaignStatus.COMPLETED.value: set(),
    CampaignStatus.PARTIALLY_COMPLETED.value: set(),
    CampaignStatus.FAILED.value: set(),
    CampaignStatus.CANCELLED.value: set(),
}


def validate_campaign_state_transition(current_status: str, target_status: str) -> bool:
    """Validates if transitioning from current_status to target_status is permitted.
    
    Normalizes status string inputs to match canonical title-cased Enum values.
    Returns True if valid. Raises InvalidCampaignStateTransitionException if invalid.
    """
    from app.core.exceptions import InvalidCampaignStateTransitionException

    if current_status == target_status:
        return True

    valid_targets = VALID_STATE_TRANSITIONS.get(current_status, set())
    if target_status not in valid_targets:
        raise InvalidCampaignStateTransitionException(
            f"Cannot transition campaign status from '{current_status}' to '{target_status}'. "
            f"Valid target statuses from '{current_status}' are: {sorted(list(valid_targets)) or 'None (Terminal state)'}"
        )
    return True
