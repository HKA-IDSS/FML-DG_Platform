from uuid import UUID, uuid4
from typing import List

import pydantic
from pydantic import PrivateAttr

from federatedmlrest.api.models.common import (BaseBsonModel, BaseModelNoExtra,
                                               PyUUID, MongoIDAndVersion)


class AddOrganisation(BaseModelNoExtra):
    """Required data to add a new organisation."""

    name: str


class Organisation(AddOrganisation, MongoIDAndVersion, BaseBsonModel):
    """Organisation, which includes users."""
    users: List[PyUUID] = pydantic.Field(default_factory=list)
