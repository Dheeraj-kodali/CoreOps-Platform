from typing import Any, Optional, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class EntityNotFoundException(AppException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found",
            code="ENTITY_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateResourceException(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(
            message=message,
            code="DUPLICATE_RESOURCE",
            status_code=status.HTTP_409_CONFLICT,
        )


class AuthenticationException(AppException):
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None):
        msg = detail or message
        super().__init__(
            message=msg,
            code="AUTHENTICATION_FAILED",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class PermissionDeniedException(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(
            message=message,
            code="PERMISSION_DENIED",
            status_code=status.HTTP_403_FORBIDDEN,
        )


class ValidationException(AppException):
    def __init__(self, message: str = "Validation error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details,
        )


class ImmutableAuditException(AppException):
    def __init__(self, message: str = "Audit records are immutable and append-only. Updates and deletions are strictly prohibited."):
        super().__init__(
            message=message,
            code="IMMUTABLE_AUDIT_VIOLATION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class BroadcastValidationException(ValidationException):
    def __init__(self, message: str = "Broadcast campaign validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            details=details,
        )


class CampaignNotFoundException(EntityNotFoundException):
    def __init__(self, campaign_id: Any):
        super().__init__(
            entity_name="BroadcastCampaign",
            identifier=campaign_id,
        )


class InvalidCampaignStateTransitionException(AppException):
    def __init__(self, message: str = "Invalid campaign status transition"):
        super().__init__(
            message=message,
            code="INVALID_STATE_TRANSITION",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class CampaignDeletionRestrictedException(AppException):
    def __init__(self, message: str = "Only campaigns in Draft status can be deleted"):
        super().__init__(
            message=message,
            code="CAMPAIGN_DELETION_RESTRICTED",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
