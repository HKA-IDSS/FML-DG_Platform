import enum
from typing import Any, Dict, List, Union, Optional
from typing_extensions import Self

import pydantic
from pydantic.types import StrictBool

from federatedmlrest.api.models.common import BaseBsonModel, MongoID, PyUUID, WithStatus
from federatedmlrest.api.models.config_models import AddConfiguration
from federatedmlrest.api.models.quality_requirements_models import AddQualityRequirement


class ProposalContent(str, enum.Enum):
    """Proposal types."""

    CONFIGURATION: str = "configuration"
    QUALITY_REQUIREMENT: str = "quality_requirement"
    INFORMATION_UPDATE: str = "information_update"
    POLICY: str = "policy"


class ProposalOperation(str, enum.Enum):
    """Proposal types."""

    CREATE: str = "create"
    UPDATE: str = "update"
    DELETE: str = "delete"


class AddProposal(BaseBsonModel):
    """Required data to add a new Proposal."""

    name: str
    proposer: Optional[PyUUID] = None
    group: PyUUID
    strategy_id: PyUUID
    content_variant: ProposalContent
    operation_variant: ProposalOperation
    proposal_content: Union[None, AddQualityRequirement, AddConfiguration]
    referenced_content: Optional[PyUUID] = None
    reasoning: str | None

    @pydantic.model_validator(mode='after')
    def check_validity_combination_content_operation(self) -> Self:
        valid_combinations = {
            "configuration": [ProposalOperation.CREATE, None],
            "quality_requirement": [ProposalOperation.CREATE, ProposalOperation.UPDATE, ProposalOperation.DELETE],
            "policy": [ProposalOperation.CREATE, ProposalOperation.UPDATE, ProposalOperation.DELETE]
        }

        if self.operation_variant not in valid_combinations[self.content_variant]:
            raise ValueError(f'Not a valid combination between content of proposal and operation.\n'
                             f'Valid operations are: {valid_combinations}')
        return self

    @pydantic.model_validator(mode='after')
    def check_existing_id_if_update_or_delete_or_none_if_create(self) -> Self:
        if self.operation_variant == ProposalOperation.CREATE and self.referenced_content is not None:
            raise ValueError(f'Creation cannot reference to an existing object')
        if ((self.operation_variant == ProposalOperation.UPDATE or self.operation_variant == ProposalOperation.DELETE)
            and self.referenced_content is None):
            raise ValueError(f'Update or delete must reference to an existing object')
        return self

    @pydantic.model_validator(mode='after')
    def check_if_content_exists_for_create_and_update(self) -> Self:
        if self.operation_variant == ProposalOperation.DELETE and self.proposal_content is not None:
            raise ValueError(f'Delete cannot have any existing content')
        if ((self.operation_variant == ProposalOperation.UPDATE or self.operation_variant == ProposalOperation.CREATE)
                and self.proposal_content is None):
            raise ValueError(f'Create and update require content')
        return self




    class Config:
        """Pydantic config."""
        use_enum_values = True  # force usage of Enum values for readability


class Vote(BaseBsonModel):
    """Vote data."""

    member: PyUUID


class PriorityVote(Vote):
    """Vote by priority."""

    priority: int = pydantic.Field(
        ge=1, le=3, description="Priority 1 is high, 3 is low."
    )


class DecisionVote(Vote):
    """Vote by decision."""

    decision: StrictBool = pydantic.Field(
        default=None, description="Decision is either True or False."
    )


class Proposal(AddProposal, MongoID, WithStatus):
    """
    Proposals represent a proposed Policy, Quality requirement or Training configuration with parameters.
    Important: A single partner within the system can be
    represented by multiple different logical member entities
    if the partner is part of multiple different groups.
    """

    votes: List[PriorityVote | DecisionVote] = pydantic.Field(default_factory=list)


class AcceptanceTally(BaseBsonModel):
    """Vote result data for boolean voting"""
    proposal: PyUUID
    accepted: bool
    votes: Dict[PyUUID, bool]
    member_count: int
    created_quality_requirement_id: PyUUID | None = None  # ID of QR created from accepted proposal


class VoteTally(BaseBsonModel):
    """Vote result data for majority voting."""

    winner: PyUUID | None
    votes: Dict[PyUUID, Any]
    member_count: int
    created_configuration_id: PyUUID | None = None  # ID of configuration created from winning proposal
    created_configuration_model_id: PyUUID | None = None  # ML model ID of created configuration
    created_configuration_dataset_id: PyUUID | None = None  # Dataset ID of created configuration
    created_configuration_group_id: PyUUID | None = None  # Group ID that owns the strategy


class TieTally(VoteTally):
    """Vote result data for majority voting."""

    winner: None
    votes: Dict[PyUUID, Any]
    member_count: int
    message: str = "There was a tie in the voting. Please, change votes to solve it."
