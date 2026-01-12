from typing import List, Optional

import pydantic

from federatedmlrest.api.models.common import (BaseModelNoExtra, MongoIDAndVersion,
                                               PyUUID)


class AddStrategy(BaseModelNoExtra):
    """Required data to add a new strategy."""

    name: str = pydantic.Field(..., description='')
    description: str | None
    comments: List[str] | None
    belonging_group: PyUUID


class Strategy(AddStrategy, MongoIDAndVersion):
    """
    Strategies can be created within a already exiting group.
    Strategies exist of quality requirements, other meta information and configurations
    can be added to a created strategy.
    Each strategy has a defined status: Proposed, Accepted or Rejected, of which Proposed the initial status is.
    """

    quality_requirements: List[PyUUID] = pydantic.Field(default_factory=list)
    quality_requirements_proposals: List[PyUUID] = pydantic.Field(default_factory=list)

    configurations: List[PyUUID] = pydantic.Field(default_factory=list)
    configuration_proposals: List[PyUUID] = pydantic.Field(default_factory=list)

    # policies: List[PyObjectId] = pydantic.Field(default_factory=list)
    # policies_proposals: List[PyObjectId] = pydantic.Field(default_factory=list)



