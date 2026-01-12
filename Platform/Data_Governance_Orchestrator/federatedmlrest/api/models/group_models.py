from typing import List, Optional
from uuid import UUID

import pydantic

from federatedmlrest.api.models.common import (BaseBsonModel, BaseModelNoExtra,
                                               PyUUID, MongoIDAndVersion)


class AddGroup(BaseModelNoExtra):
    """Required data to add a new group."""

    name: str
    description: str | None


class Group(AddGroup, MongoIDAndVersion, BaseBsonModel):
    """
    Groups are the highest organizational unit in the API's hierarchy.
    Every strategy (and thus the child elements of strategies) has to be part of a single group.
    Groups also contain members.
    """

    strategies: List[PyUUID] = pydantic.Field(default_factory=list)
    members: List[PyUUID] = pydantic.Field(default_factory=list)
