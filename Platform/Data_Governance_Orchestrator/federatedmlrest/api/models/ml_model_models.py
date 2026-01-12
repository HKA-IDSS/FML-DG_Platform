
from enum import Enum
from typing import List, Union, Literal

from pydantic import BaseModel, Field
import pydantic

from federatedmlrest.api.models.common import BaseModelNoExtra, MongoIDAndVersion

from federatedmlrest.api.models.common import PyUUID


class TypeHP(str, Enum):
    INTEGER = 'integer'
    FLOAT = 'float'
    CATEGORICAL = 'categorical'


class Hyperparameter(BaseModelNoExtra):
    """Hyperparameters are independent resources."""
    name: str
    type_of_hyperparameter: TypeHP
    valid_values: list


def return_default_list_hyperparameters_mlp():
    return [
        Hyperparameter(name="batch_size", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[16, 128]),
        Hyperparameter(name="learning_rate_init", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[1e-5, 1e-2]),
        Hyperparameter(name="decay_steps", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[500, 2000]),
        Hyperparameter(name="decay_rate", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[0.8, 0.95]),
        Hyperparameter(name="num_layers", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[1, 4]),
        Hyperparameter(name="n_units", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[4, 128]),
        Hyperparameter(name="dropout", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[0.1, 0.4]),
        Hyperparameter(name="activation", type_of_hyperparameter=TypeHP.CATEGORICAL, valid_values=["relu", "tahn"])
    ]

class MLP(BaseModelNoExtra):
    algorithm: Literal['mlp'] = 'mlp'
    hyperparameters: List[Hyperparameter] = Field(default_factory=return_default_list_hyperparameters_mlp)

def return_default_list_hyperparameters_xgboost():
    return [
        Hyperparameter(name="eta", type_of_hyperparameter=TypeHP.CATEGORICAL,
                       valid_values=[0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]),
        Hyperparameter(name="max_depth", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[2, 10]),
        Hyperparameter(name="gamma", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[0, 0.5]),
        Hyperparameter(name="max_delta_step", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[0, 10]),
        Hyperparameter(name="lambda", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[0, 1]),
        Hyperparameter(name="alpha", type_of_hyperparameter=TypeHP.FLOAT, valid_values=[0, 1]),
        Hyperparameter(name="min_child_weight", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[0, 6]),
        Hyperparameter(name="num_local_rounds", type_of_hyperparameter=TypeHP.INTEGER, valid_values=[5, 10])
    ]

class XGBoost(BaseModelNoExtra):
    algorithm: Literal['xgboost'] = 'xgboost'
    hyperparameters: List[Hyperparameter] = Field(default_factory=return_default_list_hyperparameters_xgboost)


def return_default_list_hyperparameters_custom():
    return []

class Custom(BaseModelNoExtra):
    algorithm: Literal['custom'] = 'custom'
    hyperparameters: List[Hyperparameter] = Field(default_factory=return_default_list_hyperparameters_custom)


class AddMLModel(BaseModelNoExtra):
    """Data required to add a new ML Model."""

    name: str
    strategy_governance_id: PyUUID
    model: Union[MLP, XGBoost, Custom] = Field(discriminator='algorithm')
    description: str | None
    comments: List[str] = pydantic.Field(default_factory=list)



class MLModel(AddMLModel, MongoIDAndVersion):
    """
    ML Model can be independently created and can be linked to an arbitrary amount of configurations.
    ML Models can only be deleted if they are not linked with any configuration.
    """
    pass
    # proposer: PyUUID = None
