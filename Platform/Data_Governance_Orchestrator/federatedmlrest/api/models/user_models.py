import re
from typing import Optional, Annotated

from typing import Annotated

from pydantic import AfterValidator
from federatedmlrest.api.models.common import (BaseModelNoExtra,
                                               MongoID, PyUUID, BaseBsonModel, MongoIDAndVersion)

def check_no_whitespace_in_username(name):
    matches = re.findall(r'(\s)', name)
    if len(matches) > 0:
        raise ValueError(f'{name} contains at least one whitespace. The name field must not contain any whitespaces.')
    return name

class AddUser(BaseModelNoExtra):
    """Required data to add a new user."""

    name: Annotated[str, AfterValidator(check_no_whitespace_in_username)]
    organisation_id: PyUUID
    description: str | None
    ip: Optional[str] = None


class User(AddUser, MongoIDAndVersion, BaseBsonModel):
    """User within the system and Keycloak."""


class UserName(BaseModelNoExtra):
    """Aux class for retrieving only the names of users"""
    name: str
