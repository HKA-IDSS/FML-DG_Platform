from fastapi import HTTPException
from fastapi import status as http_codes

from federatedmlrest.api import errors


class HTTPNotFoundException(HTTPException):
    """Base exception for not found resources."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=http_codes.HTTP_404_NOT_FOUND, detail=detail)


class GroupNotFoundException(HTTPNotFoundException):
    """Group not found exception."""

    def __init__(self):
        super().__init__(detail=errors.GROUP_NOT_FOUND)


class MemberNotFoundException(HTTPNotFoundException):
    """Member not found exception."""

    def __init__(self):
        super().__init__(detail=errors.MEMBER_NOT_FOUND)


class StrategyNotFoundException(HTTPNotFoundException):
    """Strategy not found exception."""

    def __init__(self):
        super().__init__(detail=errors.STRATEGY_NOT_FOUND)


class ConfigurationNotFoundException(HTTPNotFoundException):
    """Configuration not found exception."""

    def __init__(self):
        super().__init__(detail=errors.CONFIGURATION_NOT_FOUND)


class QualityRequirementNotFoundException(HTTPNotFoundException):
    """Quality Requirement not found exception."""

    def __init__(self):
        super().__init__(detail=errors.QUALITY_REQUIREMENT_NOT_FOUND)


class MLModelNotFoundException(HTTPNotFoundException):
    """ML Model not found exception."""

    def __init__(self):
        super().__init__(detail=errors.MLMODEL_NOT_FOUND)


class DatasetNotFoundException(HTTPNotFoundException):
    """Dataset not found exception."""

    def __init__(self):
        super().__init__(detail=errors.DATASET_NOT_FOUND)


class HyperparamterNotFoundException(HTTPNotFoundException):
    """Hyperparameter not found excpetion."""

    def __init__(self):
        super().__init__(detail=errors.HYPERPARAMETER_NOT_FOUND)


class ProposalNotFoundException(HTTPNotFoundException):
    """Proposal not found exception."""

    def __init__(self):
        super().__init__(detail=errors.PROPOSAL_NOT_FOUND)


class ResourceConflictException(HTTPException):
    """Base bxception for conflicting resources."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=http_codes.HTTP_409_CONFLICT, detail=detail)


class MLModelConflictException(ResourceConflictException):
    """ML Model in use exception."""

    def __init__(self):
        super().__init__(detail=errors.MLMODEL_IN_USE)


class DatasetConflictException(ResourceConflictException):
    """ML Model in use exception."""

    def __init__(self):
        super().__init__(detail=errors.DATASET_IN_USE)


class PermissionException(HTTPException):
    """User not authorized exception."""

    def __init__(self, detail: str) -> None:
        super().__init__(status_code=http_codes.HTTP_401_UNAUTHORIZED, detail=detail)


class MemberNotInGroupException(PermissionException):
    """ML Model in use exception."""

    def __init__(self):
        super().__init__(detail=errors.MEMBER_NOT_IN_GROUP)


class ConflictException(HTTPException):
    """Conflict Exception."""

    def __init__(self, detail: str):
        super().__init__(status_code=http_codes.HTTP_409_CONFLICT, detail=detail)


class BadRequestException(HTTPException):
    """Bad Request Exception."""

    def __init__(self, detail: str):
        super().__init__(status_code=http_codes.HTTP_400_BAD_REQUEST, detail=detail)


class NotProposableException(BadRequestException):
    """Proposed Object is Not Proposable."""

    def __init__(self):
        super().__init__(detail=errors.NOT_PROPOSABLE)


class UserUnauthorizedException(HTTPException):
    """User not authorized exeption."""

    def __init__(self):
        super().__init__(
            status_code=http_codes.HTTP_401_UNAUTHORIZED,
            detail=errors.INCORRECT_USER,
            headers={"WWW-Authenticate": "Basic"},
        )


class VotePriorityAlreadyExistsException(ResourceConflictException):
    """Vote with the same priority already exists."""

    def __init__(self):
        super().__init__(detail=errors.VOTE_PRIORITY_ALREADY_EXISTS)


class UserNotFoundException(HTTPNotFoundException):
    """Group not found exception."""

    def __init__(self):
        super().__init__(detail=errors.USER_NOT_FOUND)


class OrganisationNotFoundException(HTTPNotFoundException):
    """Group not found exception."""

    def __init__(self):
        super().__init__(detail=errors.ORGANISATION_NOT_FOUND)


class ModelTypeNotFound(HTTPNotFoundException):
    def __init__(self):
        super().__init__(detail=errors.MODEL_TYPE_NOT_FOUND)


class ExistingQualityRequirement(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail=errors.EXISTING_QUALITY_REQUIREMENT)


class TrainingConfigurationNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(status_code=422, detail=errors.TRAINING_CONFIGURATION_RESULTS_NOT_FOUND)