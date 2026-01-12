from typing import List, Optional, Any, Annotated, Dict

from federatedmlrest.api.models.common import BaseModelNoExtra, PyUUID, MongoID


class AddTrainingConfigurationInformation(BaseModelNoExtra):
    configuration_id: PyUUID
    metric_used: list[str]
    shapley_values: bool

class TrainingConfigurationInformation(AddTrainingConfigurationInformation, MongoID):
    pass
