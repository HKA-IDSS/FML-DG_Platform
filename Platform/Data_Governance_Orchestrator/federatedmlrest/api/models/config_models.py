from typing import Union, List, Optional
import pydantic

from federatedmlrest.api.models import dataset_models, ml_model_models, strategy_models
from federatedmlrest.api.models.common import (BaseBsonModel, MongoID,
                                               PyUUID, WithStatus, Status)


class AddConfiguration(BaseBsonModel):
    """Required data to add a new configuration."""

    ml_model_id: PyUUID
    ml_model_version: int
    dataset_id: PyUUID
    dataset_version: int
    number_of_rounds: int
    number_of_ho_rounds: int


class Configuration(AddConfiguration, MongoID, WithStatus):
    """
    Configuration Model.

    Configurations can be added to already existing strategies and have each one linked
    ML Model and one linked Dataset (ML Model and Dataset need to exist prior to the creation of the configuration).
    The linked ML Model and Dataset can be changed later.
    """
    strategy_linked: Optional[PyUUID] = None

