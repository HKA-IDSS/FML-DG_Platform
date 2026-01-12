from enum import Enum
from typing import Any, Dict, List, Optional, TypeVar, Union, Annotated

import pydantic

from federatedmlrest.api.models.common import (BaseModelNoExtra,
                                               MongoIDAndVersion)

from federatedmlrest.api.models.common import PyUUID

FT = TypeVar('FT', pydantic.StrictFloat, pydantic.StrictInt, pydantic.StrictBool, pydantic.StrictStr)


class FeatureType(str, Enum):
    """Feature types."""

    INTEGER = 'integer'
    LONG = 'long'
    FLOAT = 'float'
    DOUBLE = 'double'
    STRING = 'string'
    BOOLEAN = 'boolean'



class EncodingType(str, Enum):
    """Feature types."""
    NONE = 'none'
    ONE_HOT_ENCODER = 'one_hot_encoder'
    LABEL_ENCODER = 'label_encoder'
    STANDARD_ENCODER = 'standard_encoder'
    MIN_MAX_ENCODER = 'min_max_encoder'


class Feature(BaseModelNoExtra):
    """
    Features are a part of Datasets and are created while creating a Dataset.
    Features are currently not stored or handled as independent resources.
    """

    name: str
    type: FeatureType
    valid_values: List[FT]  # type: ignore
    # order_in_dataset: EightByteInt # Old Pydantic 1.11
    order_in_dataset: Annotated[int, pydantic.Field(strict=True, lt = 2 ** 63, gt = -(2 * 63) + 1)] # New Pydantic 2.10
    preprocessing: Optional[EncodingType] = EncodingType.NONE
    description: str | None
    group: bool
    sub_features: List[str] = pydantic.Field(default_factory=list)
    comments: List[str] = pydantic.Field(default_factory=list)

    @pydantic.model_validator(mode='before')
    def cast_integer_to_float(self):
        if self["type"] == FeatureType.FLOAT:
            self["valid_values"] = [float(number) for number in self["valid_values"]]
        if self["type"] == FeatureType.DOUBLE:
            self["valid_values"] = [float(number) for number in self["valid_values"]]
        return self

    @pydantic.model_validator(mode='after')
    def valid_types_in_valid_values(self):
        """Validate that the valid values are of the correct type."""
        type_map = {
            FeatureType.INTEGER: int,
            FeatureType.LONG: int,
            FeatureType.FLOAT: float,
            FeatureType.DOUBLE: float,
            FeatureType.STRING: str,
            FeatureType.BOOLEAN: bool,
        }

        feature_type = self.type
        as_python_type = type_map.get(feature_type, str)

        for value in self.valid_values:
            if not isinstance(value, as_python_type):
                raise ValueError(
                    f"'{value}' of type '{type(value).__name__}' in 'valid_values' "
                    f"does not match feature type '{feature_type}'. "
                    f"Did you mean '{as_python_type(value)}'?",
            )

        return self

    # @pydantic.validator('valid_combinations_feature-type_preprocessing', each_item=True, always=True)
    # def valid_combinations(cls, valu):

    class Config:
        """Pydantic config."""

        use_enum_values = True


class AddDataset(BaseModelNoExtra):
    """Data required to add a new dataset."""

    name: str
    strategy_governance_id: PyUUID
    structured: bool
    features: List[Feature]
    description: Optional[str] = pydantic.Field(default_factory=str)
    comments: Optional[List[str]] = pydantic.Field(default_factory=list)


class Dataset(AddDataset, MongoIDAndVersion):
    """
    Datasets can be independently created and can be linked to an arbitrary amount of configurations.
    Datasets contain features, which can be changed after the creation as well.
    Datasets can only be deleted if they are not linked with any configuration.
    """
    pass
    # proposer: PyUUID = None
