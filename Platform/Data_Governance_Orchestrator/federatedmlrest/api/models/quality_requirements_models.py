from enum import Enum
from typing import Union, Literal, List, Annotated
import pydantic

from federatedmlrest.api.models.common import (BaseModelNoExtra,
                                               MongoID, WithStatus, PyUUID)


class CorrectnessMethods(Enum):
    CrossEntropyLoss = "CrossEntropyLoss"
    Accuracy = "Accuracy"
    F1Score = "F1Score"
    AUC = "AUC"


class Correctness(BaseModelNoExtra):
    """Correctness Model."""

    quality_req_type: Literal["Correctness"]
    metric: CorrectnessMethods
    # possible_min_value: Annotated[float, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)] | None
    # possible_max_value: Annotated[float, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)] | None
    required_min_value: Annotated[float, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)]
    required_max_value: Annotated[float, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)]

    # Class needed to process enumerations with json.
    class Config:
        use_enum_values = True


class Bias(BaseModelNoExtra):
    """Bias Model."""

    quality_req_type: Literal["Bias"]
    vulnerable_feature: str
    accepted_threshold: Annotated[int, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)]


class Interpretability(BaseModelNoExtra):
    """Interpretability Model."""
    quality_req_type: Literal["Interpretability"]


class Robustness(BaseModelNoExtra):
    """Robustness Model."""
    quality_req_type: Literal["Robustness"]


class Efficient(BaseModelNoExtra):
    """Efficient Model."""
    quality_req_type: Literal["Efficient"]


class Security(BaseModelNoExtra):
    """Security Model."""
    quality_req_type: Literal["Security"]


class Privacy(BaseModelNoExtra):
    """Privacy Model."""
    quality_req_type: Literal['Privacy']


class UpdateQualityRequirements(BaseModelNoExtra):
    """Required data to update a quality requirement."""

    correctness: Correctness | None
    privacy: Privacy | None
    security: Security | None
    efficient: Efficient | None
    robustness: Robustness | None
    interpretability: Interpretability | None
    bias: Bias | None


class AddQualityRequirement(BaseModelNoExtra):
    quality_requirement: Union[Correctness, Bias, Interpretability, Robustness, Efficient, Security, Privacy] = (
        pydantic.Field(..., discriminator='quality_req_type')
    )


class QualityRequirement(AddQualityRequirement, MongoID):
    """
    Quality Requirements can be created within an already existing Strategy.
    Quality Requirements can either be Correctness, Bias, Intrepretability, Robustness, Efficient, Security, Privacy.
    Each Quality requirements has defined metrics, such as: possible maximum number, acceptable thresholds, etc.
    """
    # strategy_id: PyUUID
    # outdated: False
